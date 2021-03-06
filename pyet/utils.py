from numpy import tan, cos, pi, sin, arccos
from pandas import to_numeric


def day_of_year(meteoindex):
    """
    Return day of the year (1-365) based on pandas.series.index

    Parameters
    ----------
    meteoindex: pandas.Series.index

    Returns
    -------
        array of with ints specifying day of year.

    """
    return to_numeric(meteoindex.strftime('%j'))


def daylight_hours(meteoindex, lat):
    """
    Daylight hours
    Based on eq. 34 from FAO56.
    """
    j = day_of_year(meteoindex)
    sol_dec = solar_declination(j)
    sangle = sunset_angle(sol_dec, lat)
    return round(24 / pi * sangle, 1)


def sunset_angle(sol_dec, lat):
    """
    Sunset hour angle from latitude and solar declination [rad].

    Based on equations 25 in ALLen et al (1998).
    Parameters
    ----------
    sol_dec: pandas.Series
        solar declination [rad]
    lat: float/int
        the site latitude [rad]
    Returns
    -------
        pandas.Series of sunset hour angle [rad].

    """
    return arccos(-tan(sol_dec) * tan(lat))


def sunset_angle_hour(meteoindex, lz, lm, lat, sol_dec):
    """
    Sunset hour angle from latitude and solar declination [rad].

    Based on equations 25 in ALLen et al (1998).
    Parameters
    ----------
    sol_dec: pandas.Series
        solar declination [rad]
    lat: float/int
        the site latitude [rad]
    Returns
    -------
        pandas.Series of sunset hour angle [rad].

    """
    j=day_of_year(meteoindex)
    b = 2*pi*(j-81)/364
    sc = 0.1645*sin(2*b) - 0.1255*cos(b) - 0.025*sin(b)
    t = meteoindex.hour + 0.5
    sol_t = t+0.06667*(lz-lm)+sc-12
    omega = pi/12
    omega1 = omega-pi/24
    omega2 = omega+pi/24
    omegas = arccos(-tan(lat)*tan(sol_dec))
    omega1 = clip(omega1,-omegas, omegas)
    omega2 = clip(omega2,-omegas, omegas)
    omega1 = maximum(omega1,omega1, )
    omega1 = clip(omega1, -100000000, omega2)

    return omega2, omega1


def solar_declination(j):
    """
    Solar declination [rad] from day of year [rad].

    Based on equations 24 in ALLen et al (1998).
    Parameters
    ----------
    j: array.py
        day of the year (1-365)
    Returns
    -------
        array.py of solar declination [rad].

    """
    return 0.4093 * sin(2. * 3.141592654 / 365. * j - 1.39)


def relative_distance(j):
    """
    Inverse relative distance between earth and sun from day of the year.

    Based on equation 23 in Allen et al (1998).

    Parameters
    ----------
    j: array.py
        day of the year (1-365)
    Returns
    -------
        array.py specifyng day of year.
    """
    return 1 + 0.033 * cos((2. * 3.141592654 / 365.) * j)


def extraterrestrial_r(meteoindex, lat):
    """
    Returns Extraterrestrial Radiation (Ra).

    Based on equation 21 in Allen et al (1998).
    Parameters
    ----------
    meteoindex: Series.index
    lat: float/int
        the site latitude [rad]
    Returns
    -------
        Series of solar declination [rad].

    """
    j = day_of_year(meteoindex)
    dr = relative_distance(j)
    sol_dec = solar_declination(j)

    omega = sunset_angle(lat, sol_dec)
    xx = sin(sol_dec) * sin(lat)
    yy = cos(sol_dec) * cos(lat)
    return 118.08 / 3.141592654 * dr * (omega * xx + yy * sin(omega))


def extraterrestrial_r_hour(meteoindex, lat, lz=0, lm=0):
    """
    Returns Extraterrestrial Radiation (Ra).

    Based on equation 21 in Allen et al (1998).
    Parameters
    ----------
    meteoindex: Series.index
    lat: float/int
        the site latitude [rad]
    Returns
    -------
        Series of solar declination [rad].

    """
    j = day_of_year(meteoindex)
    dr = relative_distance(j)
    sol_dec = solar_declination(j)

    omega2, omega1 = sunset_angle_hour(meteoindex, lz=lz, lm=lm,
                                       lat=lat, sol_dec=sol_dec)
    xx = sin(sol_dec) * sin(lat)
    yy = cos(sol_dec) * cos(lat)
    gsc = 4.92
    return 12 / pi * gsc * dr * \
           ((omega2-omega1) * xx + yy *
            (sin(omega2)-sin(omega1)))
