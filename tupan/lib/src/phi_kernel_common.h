#ifndef __PHI_KERNEL_COMMON_H__
#define __PHI_KERNEL_COMMON_H__


#include "common.h"


#ifdef __cplusplus	// cpp only, i.e., not for OpenCL
namespace Phi {

template<size_t TILE>
struct Phi_Data_SoA {
	real_t __ALIGNED__ m[TILE];
	real_t __ALIGNED__ e2[TILE];
	real_t __ALIGNED__ rx[TILE];
	real_t __ALIGNED__ ry[TILE];
	real_t __ALIGNED__ rz[TILE];
	real_t __ALIGNED__ phi[TILE];
};

template<size_t TILE>
auto setup(
	const uint_t n,
	const real_t __m[],
	const real_t __e2[],
	const real_t __rdot[])
{
	auto ntiles = (n + TILE - 1) / TILE;
	vector<Phi_Data_SoA<TILE>> part(ntiles);
	for (size_t k = 0; k < n; ++k) {
		auto kk = k%TILE;
		auto& p = part[k/TILE];
		p.m[kk] = __m[k];
		p.e2[kk] = __e2[k];
		p.rx[kk] = __rdot[(0*NDIM+0)*n + k];
		p.ry[kk] = __rdot[(0*NDIM+1)*n + k];
		p.rz[kk] = __rdot[(0*NDIM+2)*n + k];
	}
	return part;
}

template<size_t TILE, typename PART>
void commit(const uint_t n, const PART& part, real_t __phi[])
{
	for (size_t k = 0; k < n; ++k) {
		auto kk = k%TILE;
		auto& p = part[k/TILE];
		__phi[k] = p.phi[kk];
	}
}

template<size_t TILE>
struct P2P_phi_kernel_core {
	template<typename IP, typename JP>
	void operator()(IP&& ip, JP&& jp) {
		// flop count: 16
		for (size_t i = 0; i < TILE; ++i) {
			auto iphi = ip.phi[i];
			#pragma omp simd
			for (size_t j = 0; j < TILE; ++j) {
				auto ee = ip.e2[i] + jp.e2[j];
				auto rx = ip.rx[i] - jp.rx[j];
				auto ry = ip.ry[i] - jp.ry[j];
				auto rz = ip.rz[i] - jp.rz[j];

				auto rr = ee;
				rr += rx * rx + ry * ry + rz * rz;

				auto inv_r1 = rsqrt(rr);

				jp.phi[j] -= ip.m[i] * inv_r1;

				iphi -= jp.m[j] * inv_r1;
			}
			ip.phi[i] = iphi;
		}
	}

	template<typename P>
	void operator()(P&& p) {
		// flop count: 14
		for (size_t i = 0; i < TILE; ++i) {
			#pragma omp simd
			for (size_t j = 0; j < TILE; ++j) {
				auto ee = p.e2[i] + p.e2[j];
				auto rx = p.rx[i] - p.rx[j];
				auto ry = p.ry[i] - p.ry[j];
				auto rz = p.rz[i] - p.rz[j];

				auto rr = ee;
				rr += rx * rx + ry * ry + rz * rz;

				auto inv_r1 = rsqrt(rr);
				inv_r1 = (rr > ee) ? (inv_r1):(0);

				p.phi[j] -= p.m[i] * inv_r1;
			}
		}
	}
};

}	// namespace Phi
#else


// ----------------------------------------------------------------------------


typedef struct phi_data {
	union {
		real_tn m;
		real_t _m[SIMD];
	};
	union {
		real_tn e2;
		real_t _e2[SIMD];
	};
	union {
		real_tn rx;
		real_t _rx[SIMD];
	};
	union {
		real_tn ry;
		real_t _ry[SIMD];
	};
	union {
		real_tn rz;
		real_t _rz[SIMD];
	};
	union {
		real_tn phi;
		real_t _phi[SIMD];
	};
} Phi_Data;


typedef struct phi_data_soa {
	union {
		real_tn m[LMSIZE];
		real_t _m[LMSIZE * SIMD];
	};
	union {
		real_tn e2[LMSIZE];
		real_t _e2[LMSIZE * SIMD];
	};
	union {
		real_tn rx[LMSIZE];
		real_t _rx[LMSIZE * SIMD];
	};
	union {
		real_tn ry[LMSIZE];
		real_t _ry[LMSIZE * SIMD];
	};
	union {
		real_tn rz[LMSIZE];
		real_t _rz[LMSIZE * SIMD];
	};
	union {
		real_tn phi[LMSIZE];
		real_t _phi[LMSIZE * SIMD];
	};
} Phi_Data_SoA;


static inline void
read_Phi_Data(
	uint_t base,
	uint_t lid,
	Phi_Data *p,
	uint_t n,
	global const real_t __m[],
	global const real_t __e2[],
	global const real_t __rdot[])
{
	for (uint_t k = 0, kk = base + lid;
				k < SIMD;
				k += 1, kk += WGSIZE) {
		if (kk < n) {
			p->_m[k] = __m[kk];
			p->_e2[k] = __e2[kk];
			p->_rx[k] = (__rdot+(0*NDIM+0)*n)[kk];
			p->_ry[k] = (__rdot+(0*NDIM+1)*n)[kk];
			p->_rz[k] = (__rdot+(0*NDIM+2)*n)[kk];
		}
	}
}


static inline void
simd_shuff_Phi_Data(Phi_Data *p)
{
	shuff(p->m, SIMD);
	shuff(p->e2, SIMD);
	shuff(p->rx, SIMD);
	shuff(p->ry, SIMD);
	shuff(p->rz, SIMD);
	shuff(p->phi, SIMD);
}


#endif	// __cplusplus
#endif	// __PHI_KERNEL_COMMON_H__
