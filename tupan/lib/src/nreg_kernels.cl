#include "nreg_kernels_common.h"


kernel void
nreg_Xkernel(
	uint_t const ni,
	global real_tn const __im[restrict],
	global real_tn const __irx[restrict],
	global real_tn const __iry[restrict],
	global real_tn const __irz[restrict],
	global real_tn const __ie2[restrict],
	global real_tn const __ivx[restrict],
	global real_tn const __ivy[restrict],
	global real_tn const __ivz[restrict],
	uint_t const nj,
	global real_t const __jm[restrict],
	global real_t const __jrx[restrict],
	global real_t const __jry[restrict],
	global real_t const __jrz[restrict],
	global real_t const __je2[restrict],
	global real_t const __jvx[restrict],
	global real_t const __jvy[restrict],
	global real_t const __jvz[restrict],
	real_t const dt,
	global real_tn __idrx[restrict],
	global real_tn __idry[restrict],
	global real_tn __idrz[restrict],
	global real_tn __iax[restrict],
	global real_tn __iay[restrict],
	global real_tn __iaz[restrict],
	global real_tn __iu[restrict])
{
	uint_t lid = get_local_id(0);
	uint_t gid = get_global_id(0);
	uint_t i = gid % ni;

	Nreg_X_IData ip = (Nreg_X_IData){
		.drx = 0,
		.dry = 0,
		.drz = 0,
		.ax = 0,
		.ay = 0,
		.az = 0,
		.u = 0,
		.rx = __irx[i],
		.ry = __iry[i],
		.rz = __irz[i],
		.vx = __ivx[i],
		.vy = __ivy[i],
		.vz = __ivz[i],
		.e2 = __ie2[i],
		.m = __im[i],
	};

	uint_t j = 0;

	#ifdef FAST_LOCAL_MEM
	local Nreg_X_JData _jp[LSIZE];
	#pragma unroll
	for (; (j + LSIZE - 1) < nj; j += LSIZE) {
		barrier(CLK_LOCAL_MEM_FENCE);
		_jp[lid] = (Nreg_X_JData){
			.rx = __jrx[j + lid],
			.ry = __jry[j + lid],
			.rz = __jrz[j + lid],
			.vx = __jvx[j + lid],
			.vy = __jvy[j + lid],
			.vz = __jvz[j + lid],
			.e2 = __je2[j + lid],
			.m = __jm[j + lid],
		};
		barrier(CLK_LOCAL_MEM_FENCE);
		#pragma unroll
		for (uint_t k = 0; k < LSIZE; ++k) {
			ip = nreg_Xkernel_core(ip, _jp[k], dt);
		}
	}
	#endif

	#pragma unroll
	for (uint_t k = j; k < nj; ++k) {
		Nreg_X_JData jp = (Nreg_X_JData){
			.rx = __jrx[k],
			.ry = __jry[k],
			.rz = __jrz[k],
			.vx = __jvx[k],
			.vy = __jvy[k],
			.vz = __jvz[k],
			.e2 = __je2[k],
			.m = __jm[k],
		};
		ip = nreg_Xkernel_core(ip, jp, dt);
	}

	__idrx[i] = ip.drx;
	__idry[i] = ip.dry;
	__idrz[i] = ip.drz;
	__iax[i] = ip.ax;
	__iay[i] = ip.ay;
	__iaz[i] = ip.az;
	__iu[i] = ip.m * ip.u;
}


kernel void
nreg_Vkernel(
	uint_t const ni,
	global real_tn const __im[restrict],
	global real_tn const __ivx[restrict],
	global real_tn const __ivy[restrict],
	global real_tn const __ivz[restrict],
	global real_tn const __iax[restrict],
	global real_tn const __iay[restrict],
	global real_tn const __iaz[restrict],
	uint_t const nj,
	global real_t const __jm[restrict],
	global real_t const __jvx[restrict],
	global real_t const __jvy[restrict],
	global real_t const __jvz[restrict],
	global real_t const __jax[restrict],
	global real_t const __jay[restrict],
	global real_t const __jaz[restrict],
	real_t const dt,
	global real_tn __idvx[restrict],
	global real_tn __idvy[restrict],
	global real_tn __idvz[restrict],
	global real_tn __ik[restrict])
{
	uint_t lid = get_local_id(0);
	uint_t gid = get_global_id(0);
	uint_t i = gid % ni;

	Nreg_V_IData ip = (Nreg_V_IData){
		.dvx = 0,
		.dvy = 0,
		.dvz = 0,
		.k = 0,
		.vx = __ivx[i],
		.vy = __ivy[i],
		.vz = __ivz[i],
		.ax = __iax[i],
		.ay = __iay[i],
		.az = __iaz[i],
		.m = __im[i],
	};

	uint_t j = 0;

	#ifdef FAST_LOCAL_MEM
	local Nreg_V_JData _jp[LSIZE];
	#pragma unroll
	for (; (j + LSIZE - 1) < nj; j += LSIZE) {
		barrier(CLK_LOCAL_MEM_FENCE);
		_jp[lid] = (Nreg_V_JData){
			.vx = __jvx[j + lid],
			.vy = __jvy[j + lid],
			.vz = __jvz[j + lid],
			.ax = __jax[j + lid],
			.ay = __jay[j + lid],
			.az = __jaz[j + lid],
			.m = __jm[j + lid],
		};
		barrier(CLK_LOCAL_MEM_FENCE);
		#pragma unroll
		for (uint_t k = 0; k < LSIZE; ++k) {
			ip = nreg_Vkernel_core(ip, _jp[k], dt);
		}
	}
	#endif

	#pragma unroll
	for (uint_t k = j; k < nj; ++k) {
		Nreg_V_JData jp = (Nreg_V_JData){
			.vx = __jvx[k],
			.vy = __jvy[k],
			.vz = __jvz[k],
			.ax = __jax[k],
			.ay = __jay[k],
			.az = __jaz[k],
			.m = __jm[k],
		};
		ip = nreg_Vkernel_core(ip, jp, dt);
	}

	__idvx[i] = ip.dvx;
	__idvy[i] = ip.dvy;
	__idvz[i] = ip.dvz;
	__ik[i] = ip.m * ip.k;
}

