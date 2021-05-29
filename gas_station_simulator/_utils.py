from math import floor


def _get_time_string(time: int, print_days: bool = True) -> str:
    seconds_in_a_minute = 60
    seconds_in_an_hour = 60*seconds_in_a_minute
    seconds_in_a_day = 24*seconds_in_an_hour

    left_time = time

    if print_days:
        days = floor(left_time/seconds_in_a_day)
        left_time -= days*seconds_in_a_day

    hours = floor(left_time/seconds_in_an_hour)
    left_time -= hours*seconds_in_an_hour
    minutes = floor(left_time/seconds_in_a_minute)
    left_time -= minutes*seconds_in_a_minute

    if print_days:
        current_time = f'Day {days} - {hours:02d}:{minutes:02d}:{left_time:02d}'  # noqa
    else:
        current_time = f'{hours:02d}:{minutes:02d}:{left_time:02d}'
    return current_time
