#ifndef __UNIVERSAL_KEPLER_SOLVER_H__
#define __UNIVERSAL_KEPLER_SOLVER_H__

#include "common.h"


#ifdef CONFIG_USE_DOUBLE
    #define TOLERANCE ((REAL)(2.2737367544323205948e-13))     // 2^(-42)
#else
    #define TOLERANCE ((REAL)(1.52587890625e-5))              // (2^-16)
#endif
#define MAXITER 64
#define COMPARE(x, y) (((x) > (y)) - ((x) < (y)))
#define SIGN(x) COMPARE(x, 0)


static inline REAL stumpff_c0(
//    const REAL zeta)
    REAL zeta)      // This is because of bug 4775 on old versions of glibc.
                    // That bug has already been fixed in latter versions.
{
    if (zeta < 0) {
        REAL sz = sqrt(-zeta);
        return cos(sz);
    }
    if (zeta > 0) {
        REAL sz = sqrt(zeta);
        return cosh(sz);
    }
    return ((REAL)1);
}


static inline REAL stumpff_c1(
//    const REAL zeta)
    REAL zeta)
{
    if (zeta < 0) {
        REAL sz = sqrt(-zeta);
        return sin(sz) / sz;
    }
    if (zeta > 0) {
        REAL sz = sqrt(zeta);
        return sinh(sz) / sz;
    }
    return ((REAL)1);
}


static inline REAL stumpff_c2(
//    const REAL zeta)
    REAL zeta)
{
    if (zeta < 0) {
        REAL sz = sqrt(-zeta);
        return (cos(sz) - 1) / zeta;
    }
    if (zeta > 0) {
        REAL sz = sqrt(zeta);
        return (cosh(sz) - 1) / zeta;
    }
    return 1/((REAL)2);
}


static inline REAL stumpff_c3(
//    const REAL zeta)
    REAL zeta)
{
    if (zeta < 0) {
        REAL sz = sqrt(-zeta);
        return (sin(sz) / sz - 1) / zeta;
    }
    if (zeta > 0) {
        REAL sz = sqrt(zeta);
        return (sinh(sz) / sz - 1) / zeta;
    }
    return 1/((REAL)6);
}


static inline REAL S0(
    const REAL s,
    const REAL alpha)
{
    REAL s2 = s * s;
    REAL zeta = alpha * s2;
    return stumpff_c0(zeta);
}


static inline REAL S1(
    const REAL s,
    const REAL alpha)
{
    REAL s2 = s * s;
    REAL zeta = alpha * s2;
    return s * stumpff_c1(zeta);
}


static inline REAL S2(
    const REAL s,
    const REAL alpha)
{
    REAL s2 = s * s;
    REAL zeta = alpha * s2;
    return s2 * stumpff_c2(zeta);
}


static inline REAL S3(
    const REAL s,
    const REAL alpha)
{
    REAL s2 = s * s;
    REAL s3 = s * s2;
    REAL zeta = alpha * s2;
    return s3 * stumpff_c3(zeta);
}


static inline REAL lagrange_f(
    const REAL s,
    const REAL r0,
    const REAL m,
    const REAL alpha)
{
    return 1 - m * S2(s, alpha) / r0;
}


static inline REAL lagrange_dfds(
    const REAL s,
    const REAL r0,
    const REAL r1,
    const REAL m,
    const REAL alpha)
{
    return -m * S1(s, alpha) / (r0 * r1);
}


static inline REAL lagrange_g(
    const REAL s,
    const REAL r0,
    const REAL m,
    const REAL alpha,
    const REAL dt)
{
    return dt - m * S3(s, alpha);
}


static inline REAL lagrange_dgds(
    const REAL s,
    const REAL r0,
    const REAL r1,
    const REAL m,
    const REAL alpha)
{
    return 1 - m * S2(s, alpha) / r1;
}


static inline REAL universal_kepler(
    const REAL s,
    const REAL r0,
    const REAL r0v0,
    const REAL m,
    const REAL alpha)
{
//    return r0 * S1(s, alpha) + r0v0 * S2(s, alpha) + m * S3(s, alpha);
    return r0 * s + r0v0 * S2(s, alpha) + (m + alpha * r0) * S3(s, alpha);
}


static inline REAL universal_kepler_ds(
    const REAL s,
    const REAL r0,
    const REAL r0v0,
    const REAL m,
    const REAL alpha)
{
//    return r0 * S0(s, alpha) + r0v0 * S1(s, alpha) + m * S2(s, alpha);
    return r0 + r0v0 * S1(s, alpha) + (m + alpha * r0) * S2(s, alpha);
}


static inline REAL universal_kepler_dsds(
    const REAL s,
    const REAL r0,
    const REAL r0v0,
    const REAL m,
    const REAL alpha)
{
    return r0v0 * S0(s, alpha) + (m + alpha * r0) * S1(s, alpha);
}


static inline REAL f(
    const REAL s,
    REAL *arg)
{
    return universal_kepler(s, arg[1], arg[2], arg[3], arg[4]) - arg[0];
}


static inline REAL fprime(
    const REAL s,
    REAL *arg)
{
    return universal_kepler_ds(s, arg[1], arg[2], arg[3], arg[4]);
}


static inline REAL fprimeprime(
    const REAL s,
    REAL *arg)
{
    return universal_kepler_dsds(s, arg[1], arg[2], arg[3], arg[4]);
}


#define ORDER 5
static inline INT laguerre(
    REAL x0,
    REAL *x,
    REAL *arg)
{
    INT i = 0;
    REAL delta;

    *x = x0;
    do {
        REAL fv = f(*x, arg);
        REAL dfv = fprime(*x, arg);
        REAL ddfv = fprimeprime(*x, arg);

        REAL a = dfv;
        REAL a2 = a * a;
        REAL b = a2 - fv * ddfv;
        REAL g = ORDER * fv;
        REAL h = a + SIGN(a) * sqrt(fabs((ORDER - 1) * (ORDER * b - a2)));
        if (h == 0) return -1;
        delta = -g / h;

        (*x) += delta;
        i += 1;
        if (i > MAXITER) return -2;
    } while (fabs(delta) > TOLERANCE);
    if (SIGN((*x)) != SIGN(x0)) return -3;
    return 0;
}


static inline INT halley(
    REAL x0,
    REAL *x,
    REAL *arg)
{
    INT i = 0;
    REAL delta;

    *x = x0;
    do {
        REAL fv = f(*x, arg);
        REAL dfv = fprime(*x, arg);
        REAL ddfv = fprimeprime(*x, arg);

        REAL g = 2 * fv * dfv;
        REAL h = (2 * dfv * dfv - fv * ddfv);
        if (h == 0) return -1;
        delta = -g / h;

        (*x) += delta;
        i += 1;
        if (i > MAXITER) return -2;
    } while (fabs(delta) > TOLERANCE);
    if (SIGN((*x)) != SIGN(x0)) return -3;
    return 0;
}


static inline INT newton(
    REAL x0,
    REAL *x,
    REAL *arg)
{
    INT i = 0;
    REAL delta;

    *x = x0;
    do {
        REAL fv = f(*x, arg);
        REAL dfv = fprime(*x, arg);

        REAL g = fv;
        REAL h = dfv;
        if (h == 0) return -1;
        delta = -g / h;

        (*x) += delta;
        i += 1;
        if (i > MAXITER) return -2;
    } while (fabs(delta) > TOLERANCE);
    if (SIGN((*x)) != SIGN(x0)) return -3;
    return 0;
}


static inline void set_new_pos_vel(
    const REAL dt,
    const REAL s,
    const REAL r0,
    const REAL m,
    const REAL e2,
    const REAL alpha,
    REAL *rx,
    REAL *ry,
    REAL *rz,
    REAL *vx,
    REAL *vy,
    REAL *vz)
{
    REAL r0x = *rx;
    REAL r0y = *ry;
    REAL r0z = *rz;
    REAL v0x = *vx;
    REAL v0y = *vy;
    REAL v0z = *vz;

    REAL lf = lagrange_f(s, r0, m, alpha);
    REAL lg = lagrange_g(s, r0, m, alpha, dt);
    REAL r1x, r1y, r1z;
    r1x = r0x * lf + v0x * lg;
    r1y = r0y * lf + v0y * lg;
    r1z = r0z * lf + v0z * lg;

    REAL r1sqr = r1x * r1x + r1y * r1y + r1z * r1z;
    REAL r1 = sqrt(r1sqr+e2);   // XXX: +e2

    REAL ldf = lagrange_dfds(s, r0, r1, m, alpha);
//    REAL ldg = lagrange_dgds(s, r0, r1, m, alpha);
    REAL ldg = (1 + lg * ldf) / lf;
    REAL v1x, v1y, v1z;
    v1x = r0x * ldf + v0x * ldg;
    v1y = r0y * ldf + v0y * ldg;
    v1z = r0z * ldf + v0z * ldg;

    *rx = r1x;
    *ry = r1y;
    *rz = r1z;
    *vx = v1x;
    *vy = v1y;
    *vz = v1z;
}


static inline INT _universal_kepler_solver(
    const REAL dt0,
    const REAL m,
    const REAL e2,
    const REAL r0x,
    const REAL r0y,
    const REAL r0z,
    const REAL v0x,
    const REAL v0y,
    const REAL v0z,
    REAL *r1x,
    REAL *r1y,
    REAL *r1z,
    REAL *v1x,
    REAL *v1y,
    REAL *v1z)
{
    REAL rx = r0x;
    REAL ry = r0y;
    REAL rz = r0z;
    REAL vx = v0x;
    REAL vy = v0y;
    REAL vz = v0z;

    REAL r2 = rx * rx + ry * ry + rz * rz;
    INT mask = (r2 > 0);
    if (!mask) {
        *r1x = rx;
        *r1y = ry;
        *r1z = rz;
        *v1x = vx;
        *v1y = vy;
        *v1z = vz;
        return 0;
    }
    r2 += e2;
    REAL r = sqrt(r2);

    REAL v2 = vx * vx + vy * vy + vz * vz;
    REAL rv = rx * vx + ry * vy + rz * vz;
    REAL beta = 2 - (e2 / r2);
    REAL alpha = v2 - beta * m / r;

    REAL s0, s, arg[5];

    REAL dt = dt0;
    if (alpha < 0) {
        REAL a = m/fabs(alpha);
        REAL T = 2 * PI * a * sqrt(a / m);

        REAL ratio = dt0 / T;
        dt = (ratio - (INT)(ratio)) * T;
    }

    s0 = dt / r;

    if (alpha > 0) {
        /* first guess for hyperbolic orbits:
         * adapted from formula 4.5.11 in
         * fundamentals of astrodynamics (Bate et al. 1971) */
        REAL salpha = sqrt(alpha);
        REAL ss = fabs(2 * alpha * dt / (rv + (m + alpha * r) / salpha));
        if (ss > 1) {
            s0 = SIGN(dt) * log(ss) / salpha;
        }
    }

    arg[0] = dt;
    arg[1] = r;
    arg[2] = rv;
    arg[3] = m;
    arg[4] = alpha;

//    INT err = newton(s0, &s, arg);
//    INT err = halley(s0, &s, arg);
    INT err = laguerre(s0, &s, arg);
    if (err == 0) {
        set_new_pos_vel(dt, s, r, m, e2, alpha,
                        &rx, &ry, &rz, &vx, &vy, &vz);
/*
    } else {
        rx = r0x;
        ry = r0y;
        rz = r0z;
        vx = v0x;
        vy = v0y;
        vz = v0z;
        __universal_kepler_solver(dt/2, m, e2,
                                  rx, ry, rz, vx, vy, vz,
                                  &rx, &ry, &rz, &vx, &vy, &vz);
        __universal_kepler_solver(dt/2, m, e2,
                                  rx, ry, rz, vx, vy, vz,
                                  &rx, &ry, &rz, &vx, &vy, &vz);
*/
    }

    *r1x = rx;
    *r1y = ry;
    *r1z = rz;
    *v1x = vx;
    *v1y = vy;
    *v1z = vz;
    return err;
}


static inline void __universal_kepler_solver(
    const REAL dt,
    const REAL m,
    const REAL e2,
    const REAL r0x,
    const REAL r0y,
    const REAL r0z,
    const REAL v0x,
    const REAL v0y,
    const REAL v0z,
    REAL *r1x,
    REAL *r1y,
    REAL *r1z,
    REAL *v1x,
    REAL *v1y,
    REAL *v1z)
{
    INT i, n = 1;
    REAL rx, ry, rz, vx, vy, vz;

label1:
    rx = r0x;
    ry = r0y;
    rz = r0z;
    vx = v0x;
    vy = v0y;
    vz = v0z;
    for (i = 0; i < n; ++i) {
        INT err = _universal_kepler_solver(dt/n, m, e2, rx, ry, rz, vx, vy, vz,
                                           &rx, &ry, &rz, &vx, &vy, &vz);
        if (err != 0) {
            n *= 2;
            goto label1;
        }
    }
    *r1x = rx;
    *r1y = ry;
    *r1z = rz;
    *v1x = vx;
    *v1y = vy;
    *v1z = vz;
}


static inline void universal_kepler_solver(
    const REAL dt,
    const REAL m,
    const REAL e2,
    const REAL r0x,
    const REAL r0y,
    const REAL r0z,
    const REAL v0x,
    const REAL v0y,
    const REAL v0z,
    REAL *r1x,
    REAL *r1y,
    REAL *r1z,
    REAL *v1x,
    REAL *v1y,
    REAL *v1z)
{
    REAL rx, ry, rz, vx, vy, vz;

    __universal_kepler_solver(dt, m, e2,
                              r0x, r0y, r0z, v0x, v0y, v0z,
                              &rx, &ry, &rz, &vx, &vy, &vz);

    if (e2 == 0) {
        *r1x = rx;
        *r1y = ry;
        *r1z = rz;
        *v1x = vx;
        *v1y = vy;
        *v1z = vz;
        return;
    }

    REAL r2 = r0x * r0x + r0y * r0y + r0z * r0z;
    INT mask = (r2 > 0);
    if (!mask) {
        *r1x = r0x;
        *r1y = r0y;
        *r1z = r0z;
        *v1x = v0x;
        *v1y = v0y;
        *v1z = v0z;
        return;
    }
    r2 += e2;
    REAL r = sqrt(r2);
    REAL v2 = v0x * v0x + v0y * v0y + v0z * v0z;
    REAL u0 = 2 * m / r;
    REAL e0 = v2 - u0;

    r2 = rx * rx + ry * ry + rz * rz;
    r2 += e2;
    r = sqrt(r2);
    v2 = vx * vx + vy * vy + vz * vz;
    REAL u1 = 2 * m / r;
    REAL e1 = v2 - u1;

    INT n = 1;
    REAL tol = 64*TOLERANCE;
    REAL err = fabs(e1 - e0);
    if (2*err < tol * (u1+u0)) {
        *r1x = rx;
        *r1y = ry;
        *r1z = rz;
        *v1x = vx;
        *v1y = vy;
        *v1z = vz;
        return;
    }

label1:

    n *= 2;
    rx = r0x;
    ry = r0y;
    rz = r0z;
    vx = v0x;
    vy = v0y;
    vz = v0z;

    INT i;
    for (i = 0; i < n; ++i) {
        __universal_kepler_solver(dt/n, m, e2, rx, ry, rz, vx, vy, vz,
                                  &rx, &ry, &rz, &vx, &vy, &vz);

        r2 = rx * rx + ry * ry + rz * rz;
        r2 += e2;
        r = sqrt(r2);
        v2 = vx * vx + vy * vy + vz * vz;
        u1 = 2 * m / r;
        e1 = v2 - u1;

        err = fabs(e1 - e0);
        if (2*err > tol * (u1+u0)) {
            goto label1;
        }
    }

    *r1x = rx;
    *r1y = ry;
    *r1z = rz;
    *v1x = vx;
    *v1y = vy;
    *v1z = vz;
}

#endif  // __UNIVERSAL_KEPLER_SOLVER_H__
