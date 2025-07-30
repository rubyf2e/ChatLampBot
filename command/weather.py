import click
from app_webhook import app 
import time
import configparser
from service.weather_service import WeatherService

@app.cli.command("weather")
@click.option('--sites', help='以逗號分隔的測站名稱，例如：--sites 基隆,台北')
@click.option('--all_sites', is_flag=True, help='顯示所有測站')

def weather(sites, all_sites):
    config = configparser.ConfigParser()
    config.read("config.ini")
    opendata_cwa = WeatherService(config)

    start = time.time()

    if all_sites:
        opendata_cwa = opendata_cwa.set_default_opendata_cwa()
        click.echo(opendata_cwa.get_stations_data()['A0001_URL'])
        click.echo('')
        click.echo(opendata_cwa.get_stations_data()['A0003_URL'])
    elif sites:
        click.echo("查詢以下測站的即時天氣資訊：" + sites)
        click.echo("----------------------------------------------------------------")
        sites = [s.strip() for s in sites.split(',') if s.strip()]

        for site in sites:
            click.echo(site)
            click.echo(opendata_cwa.render_station_data(opendata_cwa.get_station_weather(site)))

    end = time.time()

    click.echo("----------------------------------------------------------------")
    click.echo(f'{end-start:.3f}s 耗時')
