#ifndef __UNIVERSAL_KEPLER_SOLVER_H__
#define __UNIVERSAL_KEPLER_SOLVER_H__

#include "common.h"


static inline real_t
stumpff_c0(
	real_t const zeta)
{
	real_t abs_zeta = fabs(zeta);
	if (abs_zeta < 1) {
		/* Taylor series: 1 + z / 2 + z*z / 24 + z*z*z / 720 + ...
		 *
		 * Horner form: ((... + 1) * z / 12 + 1) * z / 2 + 1
		 *
		 * The i-th coefficient for Horner form is generated by:
		 *
		 * a_i = (2*i+2)! / (2*i)!
		 */
		return ((((((((((
		  zeta / 380 + 1)
		* zeta / 306 + 1)
		* zeta / 240 + 1)
		* zeta / 182 + 1)
		* zeta / 132 + 1)
		* zeta / 90  + 1)
		* zeta / 56  + 1)
		* zeta / 30  + 1)
		* zeta / 12  + 1)
		* zeta / 2   + 1);
	}

	real_t sz = sqrt(abs_zeta);
	if (zeta < 0) {
		return cos(sz);
	}
	return cosh(sz);
}


static inline real_t
stumpff_c1(
	real_t const zeta)
{
	real_t abs_zeta = fabs(zeta);
	if (abs_zeta < 1) {
		/* Taylor series: 1 + z / 6 + z*z / 120 + z*z*z / 5040 + ...
		 *
		 * Horner form: ((... + 1) * z / 20 + 1) * z / 6 + 1
		 *
		 * The i-th coefficient for Horner form is generated by:
		 *
		 * a_i = (2*i+3)! / (2*i+1)!
		 */
		return ((((((((((
			  zeta / 420 + 1)
			* zeta / 342 + 1)
			* zeta / 272 + 1)
			* zeta / 210 + 1)
			* zeta / 156 + 1)
			* zeta / 110 + 1)
			* zeta / 72  + 1)
			* zeta / 42  + 1)
			* zeta / 20  + 1)
			* zeta / 6   + 1);
	}

	real_t sz = sqrt(abs_zeta);
	if (zeta < 0) {
		return sin(sz) / sz;
	}
	return sinh(sz) / sz;
}


static inline real_t
stumpff_c2(
	real_t const zeta)
{
	real_t abs_zeta = fabs(zeta);
	if (abs_zeta < 1) {
		/* stumpff_c2(z) = (stumpff_c0(z) - 1) / z
		 */
		return (((((((((
			  zeta / 380 + 1)
			* zeta / 306 + 1)
			* zeta / 240 + 1)
			* zeta / 182 + 1)
			* zeta / 132 + 1)
			* zeta / 90  + 1)
			* zeta / 56  + 1)
			* zeta / 30  + 1)
			* zeta / 12  + 1) / 2;
	}

	real_t sz = sqrt(abs_zeta);
	if (zeta < 0) {
		return (cos(sz) - 1) / zeta;
	}
	return (cosh(sz) - 1) / zeta;
}


static inline real_t
stumpff_c3(
	real_t const zeta)
{
	real_t abs_zeta = fabs(zeta);
	if (abs_zeta < 1) {
		/* stumpff_c3(z) = (stumpff_c1(z) - 1) / z
		 */
		return (((((((((
			  zeta / 420 + 1)
			* zeta / 342 + 1)
			* zeta / 272 + 1)
			* zeta / 210 + 1)
			* zeta / 156 + 1)
			* zeta / 110 + 1)
			* zeta / 72  + 1)
			* zeta / 42  + 1)
			* zeta / 20  + 1) / 6;
	}

	real_t sz = sqrt(abs_zeta);
	if (zeta < 0) {
		return (sin(sz) / sz - 1) / zeta;
	}
	return (sinh(sz) / sz - 1) / zeta;
}


static inline real_t
S0(
	real_t const s,
	real_t const alpha)
{
	real_t s2 = s * s;
	real_t zeta = alpha * s2;
	return stumpff_c0(zeta);
}


static inline real_t
S1(
	real_t const s,
	real_t const alpha)
{
	real_t s2 = s * s;
	real_t zeta = alpha * s2;
	return s * stumpff_c1(zeta);
}


static inline real_t
S2(
	real_t const s,
	real_t const alpha)
{
	real_t s2 = s * s;
	real_t zeta = alpha * s2;
	return s2 * stumpff_c2(zeta);
}


static inline real_t
S3(
	real_t const s,
	real_t const alpha)
{
	real_t s2 = s * s;
	real_t s3 = s * s2;
	real_t zeta = alpha * s2;
	return s3 * stumpff_c3(zeta);
}


static inline real_t
lagrange_f(
	real_t const s,
	real_t const m,
	real_t const r0,
	real_t const alpha)
{
	return 1 - m * S2(s, alpha) / r0;
}


static inline real_t
lagrange_g(
	real_t const s,
	real_t const r0,
	real_t const r0v0,
	real_t const alpha)
{
//	return r0 * s + r0v0 * S2(s, alpha) + (alpha * r0) * S3(s, alpha);
	return r0 * S1(s, alpha) + r0v0 * S2(s, alpha);
}


static inline real_t
lagrange_dfds(
	real_t const s,
	real_t const m,
	real_t const r0,
	real_t const alpha)
{
	return -m * S1(s, alpha) / r0;
}


static inline real_t
lagrange_dgds(
	real_t const s,
	real_t const r0,
	real_t const r0v0,
	real_t const alpha)
{
//	return r0 + r0v0 * S1(s, alpha) + (alpha * r0) * S2(s, alpha);
	return r0 * S0(s, alpha) + r0v0 * S1(s, alpha);
}


static inline real_t
universal_kepler(
	real_t const s,
	real_t const m,
	real_t const r0,
	real_t const r0v0,
	real_t const alpha)
{
//	return r0 * S1(s, alpha) + r0v0 * S2(s, alpha) + m * S3(s, alpha);
	return r0 * s + r0v0 * S2(s, alpha) + (m + alpha * r0) * S3(s, alpha);
}


static inline real_t
universal_kepler_ds(
	real_t const s,
	real_t const m,
	real_t const r0,
	real_t const r0v0,
	real_t const alpha)
{
//	return r0 * S0(s, alpha) + r0v0 * S1(s, alpha) + m * S2(s, alpha);
	return r0 + r0v0 * S1(s, alpha) + (m + alpha * r0) * S2(s, alpha);
}


static inline real_t
universal_kepler_dsds(
	real_t const s,
	real_t const m,
	real_t const r0,
	real_t const r0v0,
	real_t const alpha)
{
//	return r0v0 * S0(s, alpha) + (m + alpha * r0) * S1(s, alpha);
	return r0v0 * S0(s, alpha) + (m + alpha * r0) * S1(s, alpha);
}


static inline real_t
f(
	real_t const s,
	real_t const arg[static 5])
{
	return universal_kepler(s, arg[1], arg[2], arg[3], arg[4]) - arg[0];
}


static inline real_t
fprime(
	real_t const s,
	real_t const arg[static 5])
{
	return universal_kepler_ds(s, arg[1], arg[2], arg[3], arg[4]);
}


static inline real_t
fprimeprime(
	real_t const s,
	real_t const arg[static 5])
{
	return universal_kepler_dsds(s, arg[1], arg[2], arg[3], arg[4]);
}


#define ORDER 5
static inline real_t
laguerre(
	real_t const s,
	real_t const arg[static 5])
{
	real_t fv = f(s, arg);
	real_t dfv = fprime(s, arg);
	real_t ddfv = fprimeprime(s, arg);
	real_t a = dfv;
	real_t a2 = a * a;
	real_t b = a2 - fv * ddfv;
	real_t g = ORDER * fv;
	real_t h = a + copysign(sqrt(fabs((ORDER - 1) * (ORDER * b - a2))), a);

	return -g / h;
}


static inline real_t
halley(
	real_t const s,
	real_t const arg[static 5])
{
	real_t fv = f(s, arg);
	real_t dfv = fprime(s, arg);
	real_t ddfv = fprimeprime(s, arg);
	real_t g = 2 * fv * dfv;
	real_t h = (2 * dfv * dfv - fv * ddfv);

	return -g / h;
}


static inline real_t
newton(
	real_t const s,
	real_t const arg[static 5])
{
	real_t fv = f(s, arg);
	real_t dfv = fprime(s, arg);
	real_t g = fv;
	real_t h = dfv;

	return -g / h;
}


static inline real_t
fdelta(
	real_t const s,
	real_t const arg[static 5])
{
//	return newton(s, arg);
//	return halley(s, arg);
	return laguerre(s, arg);
}


static inline int_t
findroot(
	real_t const x0,
	real_t const arg[static 5],
	real_t *x)
{
	int_t n = 0;
	real_t a, b;

	*x = x0;
	do {
		real_t delta = fdelta(*x, arg);
		if (fabs(delta) > fabs(*x))
			delta = copysign(fabs((*x)/2), delta);

		a = (*x);
		(*x) += delta;
		b = (*x);

		if (n > MAXITER) return -1;
		n += 1;
	} while (2 * fabs(b - a) > TOLERANCE * fabs(a + b));

	return 0;
}


static inline void
set_new_pos_vel(
	real_t const s,
	real_t const m,
	real_t const r0,
	real_t const r0v0,
	real_t const alpha,
	real_t const r0x,
	real_t const r0y,
	real_t const r0z,
	real_t const v0x,
	real_t const v0y,
	real_t const v0z,
	real_t *r1x,
	real_t *r1y,
	real_t *r1z,
	real_t *v1x,
	real_t *v1y,
	real_t *v1z)
{
	real_t lf = lagrange_f(s, m, r0, alpha);
	real_t lg = lagrange_g(s, r0, r0v0, alpha);

	*r1x = r0x * lf + v0x * lg;
	*r1y = r0y * lf + v0y * lg;
	*r1z = r0z * lf + v0z * lg;

	real_t ldf = lagrange_dfds(s, m, r0, alpha);
	real_t ldg = lagrange_dgds(s, r0, r0v0, alpha);

	real_t r1 = lf * ldg - lg * ldf;

	ldf /= r1;
	ldg /= r1;

	*v1x = r0x * ldf + v0x * ldg;
	*v1y = r0y * ldf + v0y * ldg;
	*v1z = r0z * ldf + v0z * ldg;
}


static inline int_t
__universal_kepler_solver(
	real_t const dt0,
	real_t const m,
	real_t const e2,
	real_t const r0x,
	real_t const r0y,
	real_t const r0z,
	real_t const v0x,
	real_t const v0y,
	real_t const v0z,
	real_t *r1x,
	real_t *r1y,
	real_t *r1z,
	real_t *v1x,
	real_t *v1y,
	real_t *v1z)
{
	*r1x = r0x;
	*r1y = r0y;
	*r1z = r0z;
	*v1x = v0x;
	*v1y = v0y;
	*v1z = v0z;

	real_t r0sqr = r0x * r0x + r0y * r0y + r0z * r0z;
	if (!(r0sqr > 0)) return 0;

	r0sqr += e2;
	real_t inv_r0 = rsqrt(r0sqr);
	real_t r0 = r0sqr * inv_r0;

	real_t r0v0 = r0x * v0x + r0y * v0y + r0z * v0z;
	real_t v0sqr = v0x * v0x + v0y * v0y + v0z * v0z;
	real_t u0sqr = 2 * m * inv_r0;
	real_t u = sqrt(u0sqr);
	real_t v = sqrt(v0sqr);
	real_t alpha0 = (v - u) * (v + u);
//	real_t alpha0 = v0sqr - u0sqr;
	real_t lagr0 = v0sqr + u0sqr;
	real_t abs_alpha0 = fabs(alpha0);

	#ifndef CONFIG_USE_OPENCL
	if (r0 * abs_alpha0 < 32 * sqrt(TOLERANCE) * m) {
		fprintf(stderr, "#---WARNING: Floating point precision "
						"used may be lower than required.\n");
		fprintf(stderr, "#---err flag: None\n");
		fprintf(stderr,
			"#   dt0: %a, m: %a, e2: %a,"
			" r0x: %a, r0y: %a, r0z: %a,"
			" v0x: %a, v0y: %a, v0z: %a\n"
			"#   r0: %a, r0v0: %a, v0sqr: %a,"
			" u0sqr: %a, alpha0: %a\n",
			dt0, m, e2,
			r0x, r0y, r0z,
			v0x, v0y, v0z,
			r0, r0v0, v0sqr,
			u0sqr, alpha0);
		fprintf(stderr, "#---\n");
	}
	#endif

	real_t s0, s, arg[5];

	real_t dt = dt0;

	/* First guess for highly hyperbolic orbits:
	 * adapted from formula 4.5.11 in fundamentals
	 * of astrodynamics (Bate et al. 1971).
	 */
	real_t ss = (2 * alpha0 * fabs(dt0 / (r0v0 + (m + alpha0 * r0) / sqrt(abs_alpha0))));
	if (ss > 1) {
		s0 = copysign(log(ss) / sqrt(abs_alpha0), dt0);
	} else {
		/* For elliptical orbits: reduce the time
		 * step to a fraction of the orbital period.
		 */
		if (alpha0 < 0) {
			real_t T = 2 * PI * m / (abs_alpha0 * sqrt(abs_alpha0));
			real_t ratio = dt0 / T;
			dt = (ratio - (int_t)(ratio)) * T;
		}
		/* This seems to work well for both
		 * elliptical and nearly parabolical
		 * orbits.
		 */
		s0 = dt * abs_alpha0 / m;

		real_t s01 = dt / r0;
		if (fabs(alpha0 * s01 * s01) < 1)
			s0 = s01;
	}

	arg[0] = dt;
	arg[1] = m;
	arg[2] = r0;
	arg[3] = r0v0;
	arg[4] = alpha0;

	int_t err = findroot(s0, arg, &s);
	if (err != 0) {
		#ifndef CONFIG_USE_OPENCL
		fprintf(stderr, "#---WARNING: Maximum iteration steps "
						"reached in 'findroot' function. Trying "
						"again with two steps of size dt0/2.\n");
		fprintf(stderr, "#---err flag: %ld\n", (long)(err));
		fprintf(stderr,
			"#   dt0: %a, m: %a, e2: %a,"
			" r0x: %a, r0y: %a, r0z: %a,"
			" v0x: %a, v0y: %a, v0z: %a\n"
			"#   dt: %a, r0: %a, r0v0: %a, v0sqr: %a, u0sqr: %a,"
			" alpha0: %a, s0: %a, s: %a, ss: %a\n",
			dt0, m, e2,
			r0x, r0y, r0z,
			v0x, v0y, v0z,
			dt, r0, r0v0, v0sqr, u0sqr,
			alpha0, s0, s, ss);
		fprintf(stderr, "#---\n");
		#endif
		return err;
	}

	real_t alpha = alpha0;
	if (e2 > 0) {
		real_t r1 = universal_kepler_ds(s, m, r0, r0v0, alpha);
		real_t inv_r = (1 / r0 + 1 / r1) / 2;
		alpha = alpha0 + m * e2 * inv_r * inv_r * inv_r;
		r1 = universal_kepler_ds(s, m, r0, r0v0, alpha);
		inv_r = (1 / r0 + 1 / r1) / 2;
		alpha = alpha0 + m * e2 * inv_r * inv_r * inv_r;
	}

	set_new_pos_vel(
		s, m, r0, r0v0, alpha,
		r0x, r0y, r0z, v0x, v0y, v0z,
		&(*r1x), &(*r1y), &(*r1z),
		&(*v1x), &(*v1y), &(*v1z));

	if (e2 > 0) {
		real_t r1sqr = *r1x * *r1x + *r1y * *r1y + *r1z * *r1z;
		real_t inv_r1 = rsqrt(r1sqr + e2);
		real_t v1sqr = *v1x * *v1x + *v1y * *v1y + *v1z * *v1z;
		real_t u1sqr = 2 * m * inv_r1;
		real_t lagr1 = v1sqr + u1sqr;
		real_t alpha1 = v1sqr - u1sqr;
		if (fabs(alpha1 - alpha0) > TOLERANCE * fabs(lagr1 + lagr0))
			return -11;
	}

	return err;
}


static inline int_t
_universal_kepler_solver(
	real_t const dt,
	real_t const m,
	real_t const e2,
	real_t const r0x,
	real_t const r0y,
	real_t const r0z,
	real_t const v0x,
	real_t const v0y,
	real_t const v0z,
	real_t *r1x,
	real_t *r1y,
	real_t *r1z,
	real_t *v1x,
	real_t *v1y,
	real_t *v1z)
{
	int_t err = __universal_kepler_solver(
			dt, m, e2,
			r0x, r0y, r0z,
			v0x, v0y, v0z,
			&(*r1x), &(*r1y), &(*r1z),
			&(*v1x), &(*v1y), &(*v1z));
	if (err == 0) return err;

	int_t n = 2;
	do {
		err = 0;
		*r1x = r0x;
		*r1y = r0y;
		*r1z = r0z;
		*v1x = v0x;
		*v1y = v0y;
		*v1z = v0z;
		for (int_t i = 0; i < n; ++i) {
			err |= __universal_kepler_solver(
					dt/n, m, e2,
					*r1x, *r1y, *r1z,
					*v1x, *v1y, *v1z,
					&(*r1x), &(*r1y), &(*r1z),
					&(*v1x), &(*v1y), &(*v1z));
		}
		if (n > MAXITER * MAXITER) return err;
		n *= 2;
	} while (err != 0);

	return err;
}


static inline int_t
universal_kepler_solver(
	real_t const dt,
	real_t const m,
	real_t const e2,
	real_t const r0x,
	real_t const r0y,
	real_t const r0z,
	real_t const v0x,
	real_t const v0y,
	real_t const v0z,
	real_t *r1x,
	real_t *r1y,
	real_t *r1z,
	real_t *v1x,
	real_t *v1y,
	real_t *v1z)
{
	int_t err = _universal_kepler_solver(
			dt, m, e2,
			r0x, r0y, r0z,
			v0x, v0y, v0z,
			&(*r1x), &(*r1y), &(*r1z),
			&(*v1x), &(*v1y), &(*v1z));
	#ifndef CONFIG_USE_OPENCL
	if (err != 0) {
		fprintf(stderr, "#---ERROR: The solution "
						"may not have converged.\n");
		fprintf(stderr, "#---err flag: %ld\n", (long)(err));
		fprintf(stderr,
			"#   dt: %a, m: %a, e2: %a,"
			" r0x: %a, r0y: %a, r0z: %a,"
			" v0x: %a, v0y: %a, v0z: %a\n",
			dt, m, e2,
			r0x, r0y, r0z,
			v0x, v0y, v0z);
		fprintf(stderr, "#---\n");
	}
	#endif

	return err;
}


#endif	// __UNIVERSAL_KEPLER_SOLVER_H__
