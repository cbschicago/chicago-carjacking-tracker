import re
import warnings
import branca
import folium
from folium.plugins import MarkerCluster  # FastMarkerCluster
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely


def _infer_latlon_from_col_names(df):
    lat_cols = []
    lon_cols = []
    for col in df.columns:
        if (
            col.lower() == "latitude"
            or col.lower().endswith("latitude")
            or col.lower() == "lat"
        ):
            lat_cols.append(col)
        elif (
            col.lower() == "longitude"
            or col.lower().endswith("longitude")
            or col.lower() == "lon"
        ):
            lon_cols.append(col)
    if len(lat_cols) == 1 and len(lon_cols) == 1:
        return lat_cols[0], lon_cols[0]
    elif len(lat_cols) == 0 or len(lon_cols) == 0:
        return None, None
    elif len(lat_cols) > 1 or len(lon_cols) > 1:
        raise ValueError(f"Multiple possible lat/lon columns found")


def _infer_latlon_cols(df):
    if isinstance(df, pd.DataFrame):
        if isinstance(df, gpd.GeoDataFrame):
            for col in df.columns:
                # prefer geometry if possible
                if col == "geometry":
                    return col
            # if no geometry col, use latlon
            lat_col, lon_col = _infer_latlon_from_col_names(df)
            return {"lat_col": lat_col, "lon_col": lon_col}
        else:
            lat_col, lon_col = _infer_latlon_from_col_names(df)
            return {"lat_col": lat_col, "lon_col": lon_col}
    else:
        raise ValueError(f"df must be of type DataFrame, not {type(df)}")


def get_fit_bounds(df, **kwargs):
    if isinstance(df, gpd.GeoDataFrame):
        geom_col = kwargs.get("geom_col", _infer_latlon_cols(df))

        assert isinstance(
            geom_col, str
        ), "Unable to identify geometry column. Pass geom_col=col"

        # geodataframe stuff
        lats = []
        lons = []
        for feature in df[geom_col]:
            if isinstance(feature, shapely.geometry.multipolygon.MultiPolygon):
                for geom in feature.geoms:
                    for lon in geom.exterior.coords.xy[0]:
                        lons.append(lon)
                    for lat in geom.exterior.coords.xy[1]:
                        lats.append(lat)
            elif isinstance(feature, shapely.geometry.polygon.Polygon):
                for lon in feature.exterior.coords.xy[0]:
                    lons.append(lon)
                for lat in feature.exterior.coords.xy[1]:
                    lats.append(lat)
            elif isinstance(feature, shapely.geometry.point.Point):
                lats.append(feature.x)
                lons.append(feature.y)
            else:
                raise ValueError(f"Unexpected geometry type in df: {type(feature)}")

        return [[min(lats), min(lons)], [max(lats), max(lons)]]

    elif isinstance(df, pd.DataFrame):
        lat_col = kwargs.get("lat_col", None)
        lon_col = kwargs.get("lon_col", None)
        # get lat and lon cols if not explicitly passed
        if all((lat_col is None, lon_col is None)):
            cols = _infer_latlon_cols(df)
            lat_col = cols["lat_col"]
            lon_col = cols["lon_col"]

            assert all(
                (lat_col is not None, lon_col is not None)
            ), "no lat col found and unable to infer"

        if df[lat_col].dtype == float:
            minlat = df[lat_col].min()
            maxlat = df[lat_col].max()
        else:
            try:
                df[lat_col] = df[lat_col].astype(float)
                minlat = df[lat_col].min()
                maxlat = df[lat_col].max()
            except ValueError:
                raise ValueError(f"Unable to coerce column {lat_col} to float")

        if df[lon_col].dtype == float:
            minlon = df[lon_col].min()
            maxlon = df[lon_col].max()
        else:
            try:
                df[lon_col] = df[lon_col].astype(float)
                minlon = df[lon_col].min()
                maxlon = df[lon_col].max()
            except ValueError:
                raise ValueError(f"Unable to coerce column {lon_col} to float")

        return [[minlat, minlon], [maxlat, maxlon]]


class Map(folium.Map):
    """A Map object

    Inherits directly from folium.Map, so folium's various mapping classes can
    be added to it using obj.add_to(), e.g. folium.Choropleth().add_to(mapper.Map).
    Also provides helpful methods for populating maps without folium's add_to syntax

    Args:
        data (pd.DataFrame, default None): data used to populate map
        lat_col (str, default None): name of column containing latitude data
            -- only necessary if Map cannot infer the columns to use
        lon_col (str, default None): name of column containing longitude data
            -- only necessary if Map cannot infer the columns to use
        geom_col (str, default None): name of pandas GeoDataFrame containing geometry
            -- only necessary if Map cannot infer the columns to use
        start_location (tuple, default None): tuple containing latitude and longitude
            -- only use if overriding the automatic fit bounds created by Map
        **kwargs: default folium args
    """

    def __init__(
        self,
        # mapper-specific
        data=None,
        lat_col=None,
        lon_col=None,
        geom_col=None,
        start_location=None,
        # folium-specific
        **kwargs,
    ):
        tiles = kwargs.get("tiles", "CartoDB Positron")
        attr = kwargs.get("attr", None)
        width = kwargs.get("width", "100%")
        height = kwargs.get("height", "100%")
        left = kwargs.get("left", "0%")
        top = kwargs.get("top", "0%")
        position = kwargs.get("position", "relative")
        min_zoom = kwargs.get("min_zoom", 0)
        max_zoom = kwargs.get("max_zoom", 18)
        zoom_start = kwargs.get("zoom_start", 10)
        min_lat = kwargs.get("min_lat", -90)
        max_lat = kwargs.get("max_lat", 90)
        min_lon = kwargs.get("min_lon", -180)
        max_lon = kwargs.get("max_lon", 180)
        max_bounds = kwargs.get("max_bounds", False)
        crs = kwargs.get("crs", "EPSG3857")
        control_scale = kwargs.get("control_scale", False)
        prefer_canvas = kwargs.get("prefer_canvas", False)
        no_touch = kwargs.get("no_touch", False)
        disable_3d = kwargs.get("disable_3d", False)
        png_enabled = kwargs.get("png_enabled", False)
        zoom_control = kwargs.get("zoom_control", True)

        folium.Map.__init__(
            self,
            location=start_location,
            width=width,
            height=height,
            left=left,
            top=top,
            position=position,
            tiles=tiles,
            attr=attr,
            min_zoom=min_zoom,
            max_zoom=max_zoom,
            zoom_start=zoom_start,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            max_bounds=max_bounds,
            crs=crs,
            control_scale=control_scale,
            prefer_canvas=prefer_canvas,
            no_touch=no_touch,
            disable_3d=disable_3d,
            png_enabled=png_enabled,
            zoom_control=zoom_control,
            **kwargs,
        )

        self.data = data
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.geom_col = geom_col

        if self.data is not None:
            assert isinstance(
                data, pd.DataFrame
            ), f"data must be of type DataFrame or GeoDataFrame, not {type(self.data)}"

            if self.lat_col is None or self.lon_col is None:
                self.lat_col, self.lon_col = _infer_latlon_from_col_names(self.data)

            geo_cols = [self.lat_col, self.lon_col, self.geom_col]
            if all(col is None for col in geo_cols):
                self.bounds = get_fit_bounds(self.data)
                self.fit_bounds(self.bounds)
            elif self.lat_col is not None and self.lon_col is not None:
                self.bounds = get_fit_bounds(
                    self.data, lat_col=self.lat_col, lon_col=self.lon_col
                )
                self.fit_bounds(self.bounds)
            elif self.geom_col is not None:
                self.bounds = get_fit_bounds(self.data, geom_col=self.geom_col)
                self.fit_bounds(self.bounds)
            elif all(col is not None for col in geo_cols):
                raise ValueError("cannot pass lat_col and lon_col with geom_col")

            if isinstance(self.data, gpd.GeoDataFrame):
                self.data_type = "GeoDataFrame"
                self.geom_col = _infer_latlon_cols(self.data)
            else:
                self.data_type = "DataFrame"

    def _has_nan_geom(self, feature):
        _point = shapely.geometry.point.Point
        _polygon = shapely.geometry.Polygon
        _multipolygon = shapely.geometry.multipolygon.MultiPolygon

        if isinstance(feature, _point):
            if pd.isna(feature.x) or pd.isna(feature.y):
                return True
            else:
                return False
        elif isinstance(feature, _polygon):
            for lon in feature.extrerior.coords.xy[0]:
                if pd.isna(lon):
                    return True
            for lat in feature.exterior.coords.xy[1]:
                if pd.isna(lat):
                    return True
            return False
        elif isinstance(feature, _multipolygon):
            for geom in feature.geoms:
                for lon in geom.exterior.coords.xy[0]:
                    if pd.isna(lon):
                        return True
                for lat in geom.exterior.coords.xy[1]:
                    if pd.isna(lat):
                        return True
            return False

    @property
    def _n_geo_records(self):
        if self.data_type == "GeoDataFrame":
            n_good_records = 0
            for feature in self.data[self.geom_col]:
                if self._has_nan_geom(feature):
                    continue
                else:
                    n_good_records += 1
            return n_good_records
        elif self.data_type == "DataFrame":
            no_nan = self.data[
                self.data[self.lat_col].notna() & self.data[self.lon_col].notna()
            ]
            return len(no_nan)

    def _parse_style_string(self, string, row):
        namespace = dict(
            zip(self.data.columns, [row[col] for col in self.data.columns])
        )
        string = string.replace("\n", "")
        if "<style>" in string:
            assert "</style>" in string, "html string contains malformed style tag"
            pat = r"<style>.*(?=<\/style)<\/style>"
            no_style = re.sub(
                pat,
                "",
                string,
                flags=re.MULTILINE,
            ).format(**namespace)
            string = re.search(pat, string).group() + no_style
        else:
            string = string.format(**namespace)
        return string

    def _add_marker(
        self,
        lat,
        lon,
        row,
        cluster=False,
        icon=None,
        draggable=False,
        # popups
        popup_html=None,
        show_popups=False,
        sticky_popups=False,
        parse_popup_html=False,
        # tooltips
        tooltip_html=None,
        tooltip_style=None,
        sticky_tooltips=True,
        **kwargs,
    ):
        if popup_html is not None:
            popup = folium.Popup(
                html=self._parse_style_string(popup_html, row),
                parse_html=parse_popup_html,
                max_width=kwargs.get("popup_max_width", "100%"),
                show=show_popups,
                sticky=sticky_popups,
            )
        else:
            popup = None

        if tooltip_html is not None:
            tooltip = folium.Tooltip(
                text=self._parse_style_string(tooltip_html, row),
                style=tooltip_style,
                sticky=sticky_tooltips,
            )
        else:
            tooltip = None

        marker = folium.Marker(
            location=[row[self.lat_col], row[self.lon_col]],
            popup=popup,
            tooltip=tooltip,
            icon=icon,
            draggable=draggable,
        )

        if cluster is False:
            marker.add_to(self)
        else:
            marker.add_to(self.cluster)

    def add_points(
        self,
        cluster=False,
        max_cluster_radius=80,
        disable_clustering_at_zoom=None,
        popup_html=None,
        tooltip_html=None,
        icon=None,
        draggable=False,
        # popup
        show_popups=False,
        sticky_popups=False,
        parse_popup_html=False,
        # tooltip
        tooltip_style=None,
        sticky_tooltips=True,
        **kwargs,
    ):
        """adds points for each row in self.data to the map

        Args: \n
            popup_html (str, default None): text to display in the popups
                -- Takes an f-string with the names of columns as variables
            tooltip_html (str, default None): text to display in the tooltips
                -- Takes an f-string with the names of columns as variables
            icon (folium icon plugin, default None): the icon plugin to use to render
            the marker. See https://getbootstrap.com/docs/3.3/components/
            for the full list
            sticky_popups {bool}: [description] (default: {False})
            parse_popup_html {bool}: [description] (default: {False})
            sticky_tooltips {bool}: [description] (default: {True})
        """

        if cluster is True:
            options = {
                "disableClusteringAtZoom": disable_clustering_at_zoom,
                "maxClusterRadius": max_cluster_radius,
            }

            self.cluster = MarkerCluster(
                options=options, max_cluster_radius=max_cluster_radius
            )
        else:
            # recommend using marker cluster between 500 and 5000
            if 500 < self._n_geo_records < 5000:
                warnings.warn(
                    "The data has more than 500 records. Consider passing "
                    "cluster=True to improve readibility"
                )
            # for really large datasets, prefer fastmarkercluster
            elif self._n_geo_records >= 5000:
                raise NotImplementedError(
                    "The data is too large to perform well. "
                    "FastMarkerCluster not implemented"
                )

        if isinstance(self.data, gpd.GeoDataFrame):
            for _, row in self.data.iterrows():
                if isinstance(row[self.geom_col], shapely.geometry.point.Point):
                    lat = row[self.geom_col].x
                    lon = row[self.geom_col].y

                    if pd.notna(abs(lat)) and pd.notna(abs(lon)):
                        self._add_marker(
                            lat=lat,
                            lon=lon,
                            row=row,
                            cluster=cluster,
                            popup_html=popup_html,
                            tooltip_html=tooltip_html,
                            parse_popup_html=parse_popup_html,
                            show_popups=show_popups,
                            popup_max_width=kwargs.get("popup_max_width"),
                            sticky_popups=sticky_popups,
                            tooltip_style=tooltip_style,
                            sticky_tooltips=sticky_tooltips,
                            icon=icon,
                            draggable=draggable,
                        )
                    else:
                        msg = (
                            "geometry contains NaN values. Rows with missing "
                            "data will be skipped"
                        )
                        warnings.warn(msg)
                        continue
                else:
                    warnings.warn(
                        "geometry contains non-shapely Point dtypes. "
                        "rows with missing data will be skipped"
                    )
                    continue

        elif isinstance(self.data, pd.DataFrame):
            for _, row in self.data.iterrows():
                # missing geometry data will throw an error
                if pd.isna(row[self.lat_col]) or pd.isna(row[self.lon_col]):
                    warnings.warn(
                        "data contains missing geo data. rows with missing geo "
                        "data will be skipped"
                    )
                    continue
                else:
                    self._add_marker(
                        lat=row[self.lat_col],
                        lon=row[self.lon_col],
                        row=row,
                        cluster=cluster,
                        popup_html=popup_html,
                        tooltip_html=tooltip_html,
                        parse_popup_html=parse_popup_html,
                        show_popups=show_popups,
                        popup_max_width=kwargs.get("popup_max_width"),
                        sticky_popups=sticky_popups,
                        tooltip_style=tooltip_style,
                        sticky_tooltips=sticky_tooltips,
                        icon=icon,
                        draggable=draggable,
                    )

        if cluster is True:
            self.cluster.add_to(self)

    def add_choropleth(
        self,
        key_on=None,
        fill_color="YlOrRd",
        data_classes=3,
        fill_opacity=0.5,
        tooltip_fields=None,
        tooltip_aliases=None,
        tooltip_style=None,
        tooltip_labels=True,
        sticky_tooltips=True,
        line_color="#FFFFFF",
        line_weight=1,
        nan_fill_color="#808080",
        highlight_fill_color=None,
        highlight_fill_opacity=None,
        highlight_line_color=None,
        highlight_line_weight=None,
        name="GeoJSON",
        show=True,
    ):
        self.geojson_objects = []

        if self.data_type != "GeoDataFrame":
            raise NotImplementedError(f"Choropleth without GeoDataFrame not supported")

        # use simple colors if no key_on column is passed
        if key_on is None:
            abbr_pat = re.compile(r"[A-Z][a-z][A-Z][a-z]")
            short_pat = re.compile(r"[A-Z][a-z]+(?=s)s")
            if abbr_pat.search(fill_color) or short_pat.search(fill_color):
                raise ValueError(
                    f"fill_color {fill_color} requires a key_on value. Pass a single "
                    "fill_color to create a choropleth without scaled colors"
                )
            else:

                def style_function(feature):
                    return {
                        "color": line_color,
                        "weight": line_weight,
                        "fillColor": fill_color,
                        "fillOpacity": fill_opacity,
                    }

                def highlight_function(feature):
                    return {
                        "color": highlight_line_color
                        if highlight_line_color
                        else line_color,
                        "weight": highlight_line_weight
                        if highlight_line_weight
                        else line_weight,
                        "fillColor": highlight_fill_color
                        if highlight_fill_color
                        else fill_color,
                        "fillOpacity": highlight_fill_opacity
                        if highlight_fill_opacity
                        else fill_opacity,
                    }

        elif key_on is not None:
            if not np.issubdtype(self.data[key_on].dtype, np.number):
                raise ValueError(
                    f"key_on dtype must be numeric, not {type(self.data[key_on].dtype)}"
                )
            else:

                def style_function(feature):
                    try:
                        scale_val = feature["properties"][key_on]
                    except KeyError:
                        raise ValueError(f"key_on {key_on} not in columns")
                    color_code = f"{fill_color}_{str(data_classes).zfill(2)}"
                    try:
                        scale = branca.colormap.linear.__dict__[color_code].scale(
                            self.data[key_on].min(), self.data[key_on].max()
                        )
                    except KeyError:
                        raise ValueError(
                            f"fill_color {color_code} not in available color palettes. "
                            "see http://colorbrewer2.org/ for help on color brewer"
                        )
                    else:
                        return {
                            "color": line_color,
                            "weight": line_weight,
                            "fillColor": nan_fill_color
                            if scale_val is None
                            else scale(scale_val),
                            "fillOpacity": fill_opacity,
                        }

                def highlight_function(feature):
                    try:
                        scale_val = feature["properties"][key_on]
                    except KeyError:
                        raise ValueError(f"key_on {key_on} not in columns")

                    if highlight_fill_color is not None:
                        highlight_color_code = (
                            f"{highlight_fill_color}_{str(data_classes).zfill(2)}"
                        )
                    else:
                        highlight_color_code = (
                            f"{fill_color}_{str(data_classes).zfill(2)}"
                        )

                    try:
                        highlight_scale = branca.colormap.linear.__dict__[
                            highlight_color_code
                        ].scale(self.data[key_on].min(), self.data[key_on].max())
                    except KeyError:
                        raise ValueError(
                            f"hightlight_fill_color {highlight_color_code} not in "
                            "available color palettes. see http://colorbrewer2.org/ "
                            "for help on color brewer"
                        )

                    else:
                        return {
                            "color": highlight_line_color
                            if highlight_line_color
                            else line_color,
                            "weight": highlight_line_weight
                            if highlight_line_weight
                            else line_weight,
                            "fillColor": nan_fill_color
                            if scale_val is None
                            else highlight_scale(scale_val),
                            "fillOpacity": highlight_fill_opacity
                            if highlight_fill_opacity
                            else fill_opacity,
                        }

        if tooltip_fields is not None:
            tooltip = folium.GeoJsonTooltip(
                fields=tooltip_fields,
                aliases=tooltip_aliases,
                labels=tooltip_labels,
                style=tooltip_style,
                sticky=sticky_tooltips,
            )
        else:
            tooltip = None

        geo_json = folium.GeoJson(
            data=self.data,
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=tooltip,
            name=name,
            show=show,
        )

        self.geojson_objects.append(geo_json)

        geo_json.add_to(self)
