from django.db.models import Min, Max, Q
from django.shortcuts import render
import json
from collections import defaultdict
from statistics import mean

from .models import KyivApartment


def get_selected_filters(request):
    selected_district = request.GET.getlist('district')
    selected_room_counts = request.GET.getlist('room_count')
    selected_floor = request.GET.getlist('floor')
    selected_built_year = request.GET.getlist('built_year')
    return selected_district, selected_room_counts, selected_floor, selected_built_year


def fetch_unique_filter_values():
    districts = KyivApartment.objects.exclude(district__isnull=True).exclude(district__exact='N/A').values_list(
        'district', flat=True).distinct().order_by('district')
    room_counts = KyivApartment.objects.exclude(room_count__isnull=True).values_list('room_count',
                                                                                     flat=True).distinct().order_by(
        'room_count')
    floors = KyivApartment.objects.exclude(floor__isnull=True).values_list('floor', flat=True).distinct().order_by(
        'floor')
    min_built_year = KyivApartment.objects.aggregate(Min('built_year'))['built_year__min']
    max_built_year = KyivApartment.objects.aggregate(Max('built_year'))['built_year__max']
    return districts, room_counts, floors, min_built_year, max_built_year


def build_year_ranges(min_built_year, max_built_year):
    return {
        f'{min_built_year}_1960': {'lt': 1960},
        '1960_1980': {'gte': 1960, 'lt': 1980},
        '1980_1990': {'gte': 1980, 'lt': 1990},
        '1990_2000': {'gte': 1990, 'lt': 2000},
        '2000_2010': {'gte': 2000, 'lt': 2010},
        f'2010_{max_built_year}': {'gte': 2010}
    }


def apply_filters(apartments, selected_district, selected_room_counts, selected_floor, selected_built_year,
                  year_ranges):
    if selected_district:
        apartments = apartments.filter(district__in=selected_district)
    if selected_room_counts:
        apartments = apartments.filter(room_count__in=selected_room_counts)
    if selected_floor:
        apartments = apartments.filter(floor__in=selected_floor)
    if selected_built_year:
        q_objects = Q()  # Create an empty Q object to hold our filter conditions
        for key in selected_built_year:
            if key in year_ranges:
                range_params = year_ranges[key]
                # Dynamically build the filter conditions and add them to the Q object
                q_objects |= Q(**{f'built_year__{lookup}': value for lookup, value in range_params.items()})
        apartments = apartments.filter(q_objects)
    return apartments


def prepare_chart_data(apartments):
    # Group apartments by publication date and calculate median prices
    grouped_apartments = defaultdict(list)
    for apt in apartments:
        date_key = apt.publication_date.strftime('%Y-%m-%d')
        grouped_apartments[date_key].append(apt.price)

    median_prices = {
        date: mean(prices)
        for date, prices in grouped_apartments.items()
    }

    # Prepare dates and prices for chart data
    dates = list(median_prices.keys())
    prices = list(median_prices.values())

    return prices, dates


def rental_price_chart(request):
    # Get selected filters from GET parameters
    selected_district, selected_room_counts, selected_floor, selected_built_year = get_selected_filters(request)

    # Fetch unique filter values
    districts, room_counts, floors, min_built_year, max_built_year = fetch_unique_filter_values()

    # Build year ranges
    year_ranges = build_year_ranges(min_built_year, max_built_year)

    # Fetch data based on selected filters
    apartments = KyivApartment.objects.all().order_by('publication_date')
    apartments = apply_filters(apartments, selected_district, selected_room_counts, selected_floor, selected_built_year,
                               year_ranges)

    # Prepare data for the chart
    prices, dates = prepare_chart_data(apartments)

    context = {
        'prices': json.dumps(prices),
        'dates': json.dumps(dates),
        'districts': districts,
        'room_counts': room_counts,
        'floors': floors,
        'min_built_year': min_built_year,
        'max_built_year': max_built_year,
        'selected_district': selected_district,
        'selected_room_count': selected_room_counts,
        'selected_floor': selected_floor,
        'selected_built_year': selected_built_year,
    }

    return render(request, 'rental_price_chart.html', context)
