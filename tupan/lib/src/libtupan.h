
void phi_kernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jrx,
    const REAL * restrict _jry,
    const REAL * restrict _jrz,
    const REAL * restrict _je2,
    REAL * restrict _iphi);

void acc_kernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jrx,
    const REAL * restrict _jry,
    const REAL * restrict _jrz,
    const REAL * restrict _je2,
    REAL * restrict _iax,
    REAL * restrict _iay,
    REAL * restrict _iaz);

void acc_jerk_kernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const REAL * restrict _ivx,
    const REAL * restrict _ivy,
    const REAL * restrict _ivz,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jrx,
    const REAL * restrict _jry,
    const REAL * restrict _jrz,
    const REAL * restrict _je2,
    const REAL * restrict _jvx,
    const REAL * restrict _jvy,
    const REAL * restrict _jvz,
    REAL * restrict _iax,
    REAL * restrict _iay,
    REAL * restrict _iaz,
    REAL * restrict _ijx,
    REAL * restrict _ijy,
    REAL * restrict _ijz);

void snap_crackle_kernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const REAL * restrict _ivx,
    const REAL * restrict _ivy,
    const REAL * restrict _ivz,
    const REAL * restrict _iax,
    const REAL * restrict _iay,
    const REAL * restrict _iaz,
    const REAL * restrict _ijx,
    const REAL * restrict _ijy,
    const REAL * restrict _ijz,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jrx,
    const REAL * restrict _jry,
    const REAL * restrict _jrz,
    const REAL * restrict _je2,
    const REAL * restrict _jvx,
    const REAL * restrict _jvy,
    const REAL * restrict _jvz,
    const REAL * restrict _jax,
    const REAL * restrict _jay,
    const REAL * restrict _jaz,
    const REAL * restrict _jjx,
    const REAL * restrict _jjy,
    const REAL * restrict _jjz,
    REAL * restrict _isx,
    REAL * restrict _isy,
    REAL * restrict _isz,
    REAL * restrict _icx,
    REAL * restrict _icy,
    REAL * restrict _icz);

void tstep_kernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const REAL * restrict _ivx,
    const REAL * restrict _ivy,
    const REAL * restrict _ivz,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jrx,
    const REAL * restrict _jry,
    const REAL * restrict _jrz,
    const REAL * restrict _je2,
    const REAL * restrict _jvx,
    const REAL * restrict _jvy,
    const REAL * restrict _jvz,
    const REAL eta,
    REAL * restrict _idt_a,
    REAL * restrict _idt_b);

void pnacc_kernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const REAL * restrict _ivx,
    const REAL * restrict _ivy,
    const REAL * restrict _ivz,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jrx,
    const REAL * restrict _jry,
    const REAL * restrict _jrz,
    const REAL * restrict _je2,
    const REAL * restrict _jvx,
    const REAL * restrict _jvy,
    const REAL * restrict _jvz,
    UINT order,
    const REAL inv1,
    const REAL inv2,
    const REAL inv3,
    const REAL inv4,
    const REAL inv5,
    const REAL inv6,
    const REAL inv7,
    REAL * restrict _ipnax,
    REAL * restrict _ipnay,
    REAL * restrict _ipnaz);

void nreg_Xkernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const REAL * restrict _ivx,
    const REAL * restrict _ivy,
    const REAL * restrict _ivz,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jrx,
    const REAL * restrict _jry,
    const REAL * restrict _jrz,
    const REAL * restrict _je2,
    const REAL * restrict _jvx,
    const REAL * restrict _jvy,
    const REAL * restrict _jvz,
    const REAL dt,
    REAL * restrict _idrx,
    REAL * restrict _idry,
    REAL * restrict _idrz,
    REAL * restrict _iax,
    REAL * restrict _iay,
    REAL * restrict _iaz,
    REAL * restrict _iu);

void nreg_Vkernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _ivx,
    const REAL * restrict _ivy,
    const REAL * restrict _ivz,
    const REAL * restrict _iax,
    const REAL * restrict _iay,
    const REAL * restrict _iaz,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jvx,
    const REAL * restrict _jvy,
    const REAL * restrict _jvz,
    const REAL * restrict _jax,
    const REAL * restrict _jay,
    const REAL * restrict _jaz,
    const REAL dt,
    REAL * restrict _idvx,
    REAL * restrict _idvy,
    REAL * restrict _idvz,
    REAL * restrict _ik);

void sakura_kernel(
    const UINT ni,
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const REAL * restrict _ivx,
    const REAL * restrict _ivy,
    const REAL * restrict _ivz,
    const UINT nj,
    const REAL * restrict _jm,
    const REAL * restrict _jrx,
    const REAL * restrict _jry,
    const REAL * restrict _jrz,
    const REAL * restrict _je2,
    const REAL * restrict _jvx,
    const REAL * restrict _jvy,
    const REAL * restrict _jvz,
    const REAL dt,
    const INT flag,
    REAL * restrict _idrx,
    REAL * restrict _idry,
    REAL * restrict _idrz,
    REAL * restrict _idvx,
    REAL * restrict _idvy,
    REAL * restrict _idvz);

void kepler_solver_kernel(
    const REAL * restrict _im,
    const REAL * restrict _irx,
    const REAL * restrict _iry,
    const REAL * restrict _irz,
    const REAL * restrict _ie2,
    const REAL * restrict _ivx,
    const REAL * restrict _ivy,
    const REAL * restrict _ivz,
    const REAL dt,
    REAL * restrict _ir1x,
    REAL * restrict _ir1y,
    REAL * restrict _ir1z,
    REAL * restrict _iv1x,
    REAL * restrict _iv1y,
    REAL * restrict _iv1z);

