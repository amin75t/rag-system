"""
Date conversion utilities for Miladi (Gregorian) to Samci (Shamsi/Jalali) dates.
"""
from datetime import datetime
from typing import Optional


class DateConverter:
    """
    Utility class for converting between Gregorian and Shamsi (Jalali) dates.
    """
    
    # Days in each month of Shamsi calendar
    SHAMSI_MONTH_DAYS = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    
    # Days in each month of Gregorian calendar
    GREGORIAN_MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    @staticmethod
    def is_gregorian_leap_year(year: int) -> bool:
        """
        Check if a Gregorian year is a leap year.
        
        Args:
            year: Gregorian year
            
        Returns:
            True if leap year, False otherwise
        """
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    @staticmethod
    def is_shamsi_leap_year(year: int) -> bool:
        """
        Check if a Shamsi year is a leap year.
        Uses a 33-year cycle where years 1, 5, 9, 13, 17, 22, 26, 30 are leap years.
        
        Args:
            year: Shamsi year
            
        Returns:
            True if leap year, False otherwise
        """
        # Simple algorithm for Shamsi leap year detection
        # This is a simplified version - for production use a library like jdatetime
        a = year % 33
        return a in [1, 5, 9, 13, 17, 22, 26, 30]
    
    @classmethod
    def miladi_to_samci(cls, year: int, month: int, day: int) -> dict:
        """
        Convert Miladi (Gregorian) date to Samci (Shamsi) date.
        
        Args:
            year: Gregorian year
            month: Gregorian month (1-12)
            day: Gregorian day
            
        Returns:
            Dictionary with 'year', 'month', 'day' keys for Shamsi date
        """
        # Calculate total days from Gregorian date
        total_days = cls._gregorian_to_days(year, month, day)
        
        # Convert to Shamsi date
        shamsi_year, shamsi_month, shamsi_day = cls._days_to_shamsi(total_days)
        
        return {
            'year': shamsi_year,
            'month': shamsi_month,
            'day': shamsi_day,
            'formatted': f"{shamsi_year}/{shamsi_month:02d}/{shamsi_day:02d}"
        }
    
    @classmethod
    def samci_to_miladi(cls, year: int, month: int, day: int) -> dict:
        """
        Convert Samci (Shamsi) date to Miladi (Gregorian) date.
        
        Args:
            year: Shamsi year
            month: Shamsi month (1-12)
            day: Shamsi day
            
        Returns:
            Dictionary with 'year', 'month', 'day' keys for Gregorian date
        """
        # Calculate total days from Shamsi date
        total_days = cls._shamsi_to_days(year, month, day)
        
        # Convert to Gregorian date
        gregorian_year, gregorian_month, gregorian_day = cls._days_to_gregorian(total_days)
        
        return {
            'year': gregorian_year,
            'month': gregorian_month,
            'day': gregorian_day,
            'formatted': f"{gregorian_year}/{gregorian_month:02d}/{gregorian_day:02d}"
        }
    
    @classmethod
    def _gregorian_to_days(cls, year: int, month: int, day: int) -> int:
        """
        Convert Gregorian date to total days since a reference point.
        Reference: March 21, 622 AD = Shamsi 1/1/1
        """
        # Days from year 1 to year-1
        days = (year - 1) * 365
        
        # Add leap days
        for y in range(1, year):
            if cls.is_gregorian_leap_year(y):
                days += 1
        
        # Add days from months in current year
        for m in range(1, month):
            days += cls.GREGORIAN_MONTH_DAYS[m - 1]
            if m == 2 and cls.is_gregorian_leap_year(year):
                days += 1
        
        # Add days
        days += day
        
        # Offset to align with Shamsi calendar
        # March 21, 622 AD is approximately day 227,000
        days -= 226894
        
        return days
    
    @classmethod
    def _shamsi_to_days(cls, year: int, month: int, day: int) -> int:
        """
        Convert Shamsi date to total days since a reference point.
        """
        # Days from year 1 to year-1
        days = (year - 1) * 365
        
        # Add leap days
        for y in range(1, year):
            if cls.is_shamsi_leap_year(y):
                days += 1
        
        # Add days from months in current year
        for m in range(1, month):
            days += cls.SHAMSI_MONTH_DAYS[m - 1]
        
        # Add days
        days += day
        
        return days
    
    @classmethod
    def _days_to_shamsi(cls, total_days: int) -> tuple:
        """
        Convert total days to Shamsi date.
        """
        year = 1
        month = 1
        day = 1
        
        # Calculate year
        while True:
            days_in_year = 366 if cls.is_shamsi_leap_year(year) else 365
            if total_days > days_in_year:
                total_days -= days_in_year
                year += 1
            else:
                break
        
        # Calculate month
        for days_in_month in cls.SHAMSI_MONTH_DAYS:
            if total_days > days_in_month:
                total_days -= days_in_month
                month += 1
            else:
                break
        
        day = total_days
        
        return year, month, day
    
    @classmethod
    def _days_to_gregorian(cls, total_days: int) -> tuple:
        """
        Convert total days to Gregorian date.
        """
        # Add offset
        total_days += 226894
        
        year = 1
        month = 1
        day = 1
        
        # Calculate year
        while True:
            days_in_year = 366 if cls.is_gregorian_leap_year(year) else 365
            if total_days > days_in_year:
                total_days -= days_in_year
                year += 1
            else:
                break
        
        # Calculate month
        for m in range(1, 13):
            days_in_month = cls.GREGORIAN_MONTH_DAYS[m - 1]
            if m == 2 and cls.is_gregorian_leap_year(year):
                days_in_month += 1
            
            if total_days > days_in_month:
                total_days -= days_in_month
                month += 1
            else:
                break
        
        day = total_days
        
        return year, month, day


def miladi_to_samci_date(date: datetime) -> dict:
    """
    Convenience function to convert a datetime object to Shamsi date.
    
    Args:
        date: datetime object
        
    Returns:
        Dictionary with Shamsi date
    """
    return DateConverter.miladi_to_samci(date.year, date.month, date.day)


def samci_to_miladi_date(year: int, month: int, day: int) -> datetime:
    """
    Convenience function to convert Shamsi date to datetime object.
    
    Args:
        year: Shamsi year
        month: Shamsi month
        day: Shamsi day
        
    Returns:
        datetime object
    """
    result = DateConverter.samci_to_miladi(year, month, day)
    return datetime(result['year'], result['month'], result['day'])
