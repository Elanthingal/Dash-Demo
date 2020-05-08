import json
import pandas as pd
import plotly.express as px

from app import _config


class Map:

    def __init__(self):
        self._geo_json = self.__read_geo_json()

    def __read_geo_json(self):
        with open(_config.GEO_JSON) as geo_file:
            geo_json = json.load(geo_file)
        return geo_json


class ScatterPlot(Map):

    def __not_affeccted_city(self, state_responses, pts=list()):
        for feature in self._geo_json['features']:
            if feature['geometry']['type'] == 'Polygon' and not feature['properties']['Dist_Name'] in list(
                    state_responses):
                pts.extend(feature['geometry']['coordinates'][0])
                pts.append([None, None])  # mark the end of a polygon

            elif feature['geometry']['type'] == 'MultiPolygon' and not feature['properties']['Dist_Name'] in list(
                    state_responses):
                for polyg in feature['geometry']['coordinates']:
                    pts.extend(polyg[0])
                    pts.append([None, None])  # end of polygon
        X, Y = zip(*pts)
        return dict(type='scatter',
                    x=X,
                    y=Y,
                    mode='lines',
                    line=dict(width=.5, color='black', opacity=1))

    def __affected_city(self, city, state_responses, state_cases, arcs=list()):

        for feature in self._geo_json['features']:

            if feature['geometry']['type'] == 'Polygon' and feature['properties']['Dist_Name'] == city:
                arcs.extend(feature['geometry']['coordinates'][0])
                arcs.append([None, None])

            elif feature['geometry']['type'] == 'MultiPolygon' and feature['properties']['Dist_Name'] == city:
                for polyg in feature['geometry']['coordinates']:
                    arcs.extend(polyg[0])
                    arcs.append([None, None])
        x, y = zip(*arcs)
        print(city, state_responses[city]['confirmed'])
        return dict(
            type='scatter',
            x=x,
            y=y,
            name=city,
            mode='lines',
            line=dict(width=.5, color='black'),
            fill="toself",
            hoverinfo="skip",
            opacity=(float(state_responses[city]['confirmed']) / float(sum(state_cases)))
        )

    def generate_map(self, state_responses, state_cases):
        data = [self.__affected_city(city, state_responses, state_cases) for city in list(state_responses)]
        data.append(self.__not_affeccted_city(state_responses))
        axis_style = dict(showline=False,
                          mirror=False,
                          showgrid=False,
                          zeroline=False,
                          ticks='',
                          showticklabels=False)
        layout = dict(title='Tamil Nadu Heat Map',
                      width=500, height=500,
                      autosize=True,
                      xaxis=axis_style,
                      yaxis=axis_style,
                      showlegend=False,
                      )
        return dict(data=data, layout=layout)


class ChoroplethMap(Map):

    def __get_missing_cities(self, state_responses):
        _missing_states = [city for city in
                           [self._geo_json['features'][idx]['properties']['district'] for idx in
                            range(len(self._geo_json['features']))] if city not in list(state_responses)]

        return _missing_states, [0 for _ in range(len(_missing_states))]

    def __get_data_frame(self, state_responses):
        missing_cities, count = self.__get_missing_cities(state_responses)
        city_list = list(state_responses)
        counts = [state_responses[idx]['confirmed'] for idx in city_list]
        city_list.extend(missing_cities)
        counts.extend(count)
        return pd.DataFrame(data=dict(District=city_list, Confirmed=counts))

    def generate_map(self, state_responses):
        df = self.__get_data_frame(state_responses)
        fig = px.choropleth_mapbox(data_frame=df,
                                   geojson=self._geo_json,
                                   color="Confirmed",
                                   locations="District",
                                   color_continuous_scale='gray_r',
                                   featureidkey="properties.district",
                                   center={"lat": 11.127123, "lon": 78.656891},
                                   hover_name="District",
                                   mapbox_style="white-bg", zoom=5.5, opacity=0.7)
        fig.update_layout(title_text="Heat Map", width=500, height=550)
        fig.update_geos(fitbounds="locations", visible=False)
        return fig
