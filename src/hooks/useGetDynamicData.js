import { useEffect, useState } from "react";
import axios from "axios";

function useGetDynamicData(backend_url, viewState) {
  const [dynamicData, setDynamicData] = useState({
    status: "not_started",
    data: [],
  });

  const [parametersToQuery, setParametersToQuery] = useState(null);

  useEffect(() => {
    if (
      !parametersToQuery ||
      Math.abs(
        viewState.min_x < parametersToQuery.min_x ||
          viewState.max_x > parametersToQuery.max_x ||
          viewState.min_y < parametersToQuery.min_y ||
          viewState.max_y > parametersToQuery.max_y ||
          Math.abs(viewState.zoom[0] - parametersToQuery.zoom[0]) > 1 ||
          Math.abs(viewState.zoom[1] - parametersToQuery.zoom[1]) > 1
      )
    ) {
      setParametersToQuery({
        min_x: viewState.min_x,
        max_x: viewState.max_x,
        min_y: viewState.min_y,
        max_y: viewState.max_y,
        zoom: viewState.zoom,
      });
    }
  }, [viewState, parametersToQuery]);

  useEffect(() => {
    if (!parametersToQuery) return;
    if (dynamicData.status === "loading") {
      return;
    }
    // Make call to backend to get data
    let url = backend_url + "/nodes/?type=leaves";
    if (
      parametersToQuery.min_x &&
      parametersToQuery.max_x &&
      parametersToQuery.min_y &&
      parametersToQuery.max_y
    ) {
      url =
        url +
        "&min_x=" +
        parametersToQuery.min_x +
        "&max_x=" +
        parametersToQuery.max_x +
        "&min_y=" +
        parametersToQuery.min_y +
        "&max_y=" +
        parametersToQuery.max_y;
    }

    let query_precision = {
      x: parametersToQuery.zoom[0],
      y: parametersToQuery.zoom[1],
    };

    url =
      url +
      "&x_precision=" +
      query_precision.x +
      "&y_precision=" +
      query_precision.y;

    axios.get(url).then(function (response) {
      console.log("got data", response.data);
      setDynamicData({
        status: "loaded",
        data: response.data,
      });
    });
    setDynamicData({ ...dynamicData, status: "loading" });
  }, [parametersToQuery, backend_url]);

  return dynamicData;
}

export default useGetDynamicData;