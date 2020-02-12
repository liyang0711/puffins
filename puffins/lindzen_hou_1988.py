#! /usr/bin/env python
"""Expressions from (and extending) Lindzen and Hou 1988."""

import numpy as np

from .constants import (
    C_P,
    DELTA_H,
    DELTA_V,
    GRAV_EARTH,
    HEIGHT_TROPO,
    P0,
    R_D,
    RAD_EARTH,
    ROT_RATE_EARTH,
    TEMP_TROPO,
    THETA_REF,
)
from .names import LAT_STR
from .nb_utils import cosdeg, sindeg, zero_cross_nh
from .dynamics import abs_vort_from_u, therm_ross_num
from .fixed_temp_tropo import (
    DTHETA_DTS_MOIST,
    GAMMA_MOIST,
    grad_wind_bouss_fixed_temp_tropo,
)


def pot_temp_rce_lh88(lats, lat_max, z=0.5*HEIGHT_TROPO, theta_ref=THETA_REF,
                      height=HEIGHT_TROPO, delta_h=DELTA_H, delta_v=DELTA_V):
    """Eq. (1b) of Lindzen and Hou 1988."""
    return theta_ref*(1 + delta_h/3 *
                      (1 - 3*(sindeg(lats) - sindeg(lat_max))**2) +
                      (z/height - 0.5)*delta_v)


def dtheta_rce_lh88_dlat(lats, lat_max, delta_h):
    """Meridional derivative of RCE potential temperature.

    Note that this includes the 1/theta_ref factor.

    """
    return -2 * delta_h * cosdeg(lats) * (sindeg(lats) - sindeg(lat_max))


def u_rce_lh88(lats, lat_max, thermal_ro, rot_rate=ROT_RATE_EARTH,
               radius=RAD_EARTH):
    """Gradient balance wind for the Lindzen and Hou 1988 forcing."""
    return ((((1 + 2*thermal_ro*(1 - sindeg(lat_max) / sindeg(lats))) ** 0.5)
             - 1)*rot_rate*radius*cosdeg(lats))


def crit_vort_metric_rce_lh88(lat, ascent_lat, delta_h, height,
                              grav=GRAV_EARTH, rot_rate=ROT_RATE_EARTH,
                              radius=RAD_EARTH):
    """Analytical solution for PH92 criticality applied to LH88 forcing."""
    thermal_ro = therm_ross_num(delta_h, height, grav, rot_rate, radius)
    coslat = cosdeg(lat)
    sinlat = sindeg(lat)
    return (-2*rot_rate**2*radius**2*coslat**3*sinlat *
            (2 + thermal_ro*(4 - sindeg(ascent_lat) / sinlat *
                             (3 + sinlat ** -2))))


def abs_vort_norm_rce_lh88(lat, lat_max, delta_h=1./6., height=HEIGHT_TROPO,
                           grav=GRAV_EARTH, rot_rate=ROT_RATE_EARTH,
                           radius=RAD_EARTH, thermal_ro=None):
    """Analytical solution for absolute vorticity of LH88 forcing."""
    if thermal_ro is None:
        thermal_ro = therm_ross_num(delta_h, height, grav, rot_rate, radius)
    coslat = cosdeg(lat)
    sinlat = sindeg(lat)
    sin_latmax = sindeg(lat_max)
    power_arg = 1 + 2*thermal_ro*(1 - sin_latmax / sinlat)
    term1 = power_arg**0.5
    term2 = 2*sinlat - (thermal_ro*(coslat**2)*sin_latmax /
                        ((sinlat**2)*power_arg))
    return term1*term2


def eta_rce_lh88_zero_cross(lats, lat_max, delta_h=DELTA_H,
                            height=HEIGHT_TROPO, rot_rate=ROT_RATE_EARTH,
                            radius=RAD_EARTH, grav=GRAV_EARTH,
                            lat_str=LAT_STR):
    thermal_ro = therm_ross_num(
        delta_h,
        height,
        grav=grav,
        rot_rate=rot_rate,
        radius=radius,
    )
    u_rce = u_rce_lh88(
        lats,
        lat_max,
        thermal_ro,
        rot_rate=rot_rate,
        radius=radius,
    )
    eta_rce = abs_vort_from_u(
        u_rce,
        rot_rate=rot_rate,
        radius=radius,
        lat_str=lat_str,
    )
    return zero_cross_nh(eta_rce, lat_str=lat_str)


def lapse_rate_rce_lh88(lat, lat_max, z, theta_ref=THETA_REF,
                        height=HEIGHT_TROPO, delta_h=DELTA_H, delta_v=DELTA_V,
                        r_d=R_D, c_p=C_P, grav=GRAV_EARTH):
    """dT/dz for Lindzen and Hou 1988 forcing."""
    pot_temp = pot_temp_rce_lh88(lat, lat_max, z=z, theta_ref=theta_ref,
                                 height=height, delta_h=delta_h,
                                 delta_v=delta_v)
    pot_temp_z0 = pot_temp_rce_lh88(lat, lat_max, z=0, theta_ref=theta_ref,
                                    height=height, delta_h=delta_h,
                                    delta_v=delta_v)
    gamma_dry = grav / c_p
    dpot_temp_dz = theta_ref * delta_v / height
    return dpot_temp_dz - gamma_dry*(1 + np.log(pot_temp / pot_temp_z0))


def pressure_rce_lh88(lat, lat_max, z, theta_ref=THETA_REF,
                      height=HEIGHT_TROPO, delta_h=DELTA_H, delta_v=DELTA_V,
                      p0=P0, r_d=R_D, c_p=C_P, grav=GRAV_EARTH):
    """Equilibrium pressure field for Lindzen and Hou 1988 forcing."""
    pot_temp = pot_temp_rce_lh88(lat, lat_max, z=z, theta_ref=theta_ref,
                                 height=height, delta_h=delta_h,
                                 delta_v=delta_v)
    pot_temp_z0 = pot_temp_rce_lh88(lat, lat_max, z=0, theta_ref=theta_ref,
                                    height=height, delta_h=delta_h,
                                    delta_v=delta_v)
    gamma_dry = grav / c_p
    dpot_temp_dz = theta_ref * delta_v / height
    leading_factor = gamma_dry / dpot_temp_dz
    kappa_inv = c_p / r_d
    return p0*(1 - leading_factor*np.log(pot_temp / pot_temp_z0))**kappa_inv


# Modified by assuming fixed lapse rate and/or tropopause temperature.
def u_rce_lh88_fixed_trop_temp(lats, lat_max, theta_ref=THETA_REF,
                               delta_h=DELTA_H, temp_tropo=TEMP_TROPO,
                               gamma=GAMMA_MOIST, dtheta_dts=DTHETA_DTS_MOIST,
                               rot_rate=ROT_RATE_EARTH, radius=RAD_EARTH,
                               grav=GRAV_EARTH, c_p=C_P, compute_temp_sfc=True,
                               lat_str=LAT_STR):
    """Lindzen and Hou 1988 RCE zonal wind for fixed tropopause temperature."""
    theta = pot_temp_rce_lh88(
        lats,
        lat_max,
        z=0.5,
        theta_ref=theta_ref,
        height=1,
        delta_h=delta_h,
    )
    return grad_wind_bouss_fixed_temp_tropo(
        lats,
        theta,
        theta_ref=theta_ref,
        temp_tropo=temp_tropo,
        gamma=gamma,
        dtheta_dts=dtheta_dts,
        rot_rate=rot_rate,
        radius=radius,
        grav=grav,
        c_p=c_p,
        compute_temp_sfc=compute_temp_sfc,
        lat_str=lat_str,
    )


def eta_rce_lh88_fixed_tt_zero_cross(lats, lat_max, theta_ref=THETA_REF,
                                     delta_h=DELTA_H, temp_tropo=TEMP_TROPO,
                                     gamma=GAMMA_MOIST,
                                     dtheta_dts=DTHETA_DTS_MOIST,
                                     rot_rate=ROT_RATE_EARTH, radius=RAD_EARTH,
                                     grav=GRAV_EARTH, c_p=C_P,
                                     compute_temp_sfc=True, lat_str=LAT_STR):
    """Lindzen and Hou 1988 RCE absolute vorticity zero crossing.

    Assumes fixed tropopause temperature in calculation of zonal wind.

    """
    u_rce = u_rce_lh88_fixed_trop_temp(
        lats,
        lat_max,
        theta_ref=theta_ref,
        delta_h=delta_h,
        temp_tropo=temp_tropo,
        gamma=gamma,
        dtheta_dts=dtheta_dts,
        rot_rate=rot_rate,
        radius=radius,
        grav=grav,
        c_p=c_p,
        compute_temp_sfc=compute_temp_sfc,
        lat_str=lat_str,
    )
    eta_rce = abs_vort_from_u(
        u_rce,
        rot_rate=rot_rate,
        radius=radius,
        lat_str=lat_str,
    )
    return zero_cross_nh(eta_rce, lat_str=lat_str)


if __name__ == '__main__':
    pass