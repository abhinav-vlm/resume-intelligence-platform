def merge_intervals(intervals: list[tuple]) -> list[tuple]:
    merged = []
    converted = []
    for interval in intervals:
        month_index_0 = interval[0][0]*12 + interval[0][1]
        month_index_1 = interval[1][0]*12 + interval[1][1]
        if not merged:
            merged.append((month_index_0,month_index_1))
            continue
        if month_index_0 <= merged[-1][1]+1:
            if month_index_1 <= merged[-1][1]:
                continue
            else:
                merged[-1] = (merged[-1][0], month_index_1)
        else:
            merged.append((month_index_0,month_index_1))
    for start_index,end_index in merged:
        start_month = (start_index-1)%12+1
        start_year = (start_index-1)//12
        end_month = (end_index-1)%12+1
        end_year = (end_index-1)//12
        converted.append(((start_year,start_month),(end_year,end_month)))
    return converted