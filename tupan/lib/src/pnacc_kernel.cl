#include "pnacc_kernel_common.h"


kernel void
pnacc_kernel(
	const uint_t ni,
	global const real_tn __im[restrict],
	global const real_tn __irx[restrict],
	global const real_tn __iry[restrict],
	global const real_tn __irz[restrict],
	global const real_tn __ie2[restrict],
	global const real_tn __ivx[restrict],
	global const real_tn __ivy[restrict],
	global const real_tn __ivz[restrict],
	const uint_t nj,
	global const real_t __jm[restrict],
	global const real_t __jrx[restrict],
	global const real_t __jry[restrict],
	global const real_t __jrz[restrict],
	global const real_t __je2[restrict],
	global const real_t __jvx[restrict],
	global const real_t __jvy[restrict],
	global const real_t __jvz[restrict],
//	const CLIGHT clight,
	constant const CLIGHT * restrict clight,
	global real_tn __ipnax[restrict],
	global real_tn __ipnay[restrict],
	global real_tn __ipnaz[restrict])
{
	uint_t lid = get_local_id(0);
	uint_t gid = get_global_id(0);
	uint_t i = gid % ni;

	PNAcc_IData ip = (PNAcc_IData){
		.pnax = 0,
		.pnay = 0,
		.pnaz = 0,
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
	local PNAcc_JData _jp[LSIZE];
	#pragma unroll
	for (; (j + LSIZE - 1) < nj; j += LSIZE) {
		barrier(CLK_LOCAL_MEM_FENCE);
		_jp[lid] = (PNAcc_JData){
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
			ip = pnacc_kernel_core(ip, _jp[k], *clight);
		}
	}
	#endif

	#pragma unroll
	for (uint_t k = j; k < nj; ++k) {
		PNAcc_JData jp = (PNAcc_JData){
			.rx = __jrx[k],
			.ry = __jry[k],
			.rz = __jrz[k],
			.vx = __jvx[k],
			.vy = __jvy[k],
			.vz = __jvz[k],
			.e2 = __je2[k],
			.m = __jm[k],
		};
		ip = pnacc_kernel_core(ip, jp, *clight);
	}

	__ipnax[i] = ip.pnax;
	__ipnay[i] = ip.pnay;
	__ipnaz[i] = ip.pnaz;
}

