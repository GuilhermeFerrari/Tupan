#include "nreg_kernels_common.h"


void
nreg_Xkernel(
	const uint_t ni,
	const real_t __im[],
	const real_t __irx[],
	const real_t __iry[],
	const real_t __irz[],
	const real_t __ie2[],
	const real_t __ivx[],
	const real_t __ivy[],
	const real_t __ivz[],
	const uint_t nj,
	const real_t __jm[],
	const real_t __jrx[],
	const real_t __jry[],
	const real_t __jrz[],
	const real_t __je2[],
	const real_t __jvx[],
	const real_t __jvy[],
	const real_t __jvz[],
	const real_t dt,
	real_t __idrx[],
	real_t __idry[],
	real_t __idrz[],
	real_t __iax[],
	real_t __iay[],
	real_t __iaz[],
	real_t __iu[])
{
	for (uint_t i = 0; i < ni; ++i) {
		Nreg_X_Data ip = (Nreg_X_Data){
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

		for (uint_t j = 0; j < nj; ++j) {
			Nreg_X_Data jp = (Nreg_X_Data){
				.drx = 0,
				.dry = 0,
				.drz = 0,
				.ax = 0,
				.ay = 0,
				.az = 0,
				.u = 0,
				.rx = __jrx[j],
				.ry = __jry[j],
				.rz = __jrz[j],
				.vx = __jvx[j],
				.vy = __jvy[j],
				.vz = __jvz[j],
				.e2 = __je2[j],
				.m = __jm[j],
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
}


void
nreg_Vkernel(
	const uint_t ni,
	const real_t __im[],
	const real_t __ivx[],
	const real_t __ivy[],
	const real_t __ivz[],
	const real_t __iax[],
	const real_t __iay[],
	const real_t __iaz[],
	const uint_t nj,
	const real_t __jm[],
	const real_t __jvx[],
	const real_t __jvy[],
	const real_t __jvz[],
	const real_t __jax[],
	const real_t __jay[],
	const real_t __jaz[],
	const real_t dt,
	real_t __idvx[],
	real_t __idvy[],
	real_t __idvz[],
	real_t __ik[])
{
	for (uint_t i = 0; i < ni; ++i) {
		Nreg_V_Data ip = (Nreg_V_Data){
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

		for (uint_t j = 0; j < nj; ++j) {
			Nreg_V_Data jp = (Nreg_V_Data){
				.dvx = 0,
				.dvy = 0,
				.dvz = 0,
				.k = 0,
				.vx = __jvx[j],
				.vy = __jvy[j],
				.vz = __jvz[j],
				.ax = __jax[j],
				.ay = __jay[j],
				.az = __jaz[j],
				.m = __jm[j],
			};
			ip = nreg_Vkernel_core(ip, jp, dt);
		}

		__idvx[i] = ip.dvx;
		__idvy[i] = ip.dvy;
		__idvz[i] = ip.dvz;
		__ik[i] = ip.m * ip.k;
	}
}

