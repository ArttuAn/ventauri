(function (global) {
  "use strict";

  function formatActivityEvent(e) {
    var det = "";
    try {
      if (e.detail && Object.keys(e.detail).length) {
        det = " | " + JSON.stringify(e.detail);
      }
    } catch (x) {
      det = "";
    }
    var job = e.job_id ? " job=" + String(e.job_id).slice(0, 8) : "";
    var sess = e.session_id ? " sess=" + String(e.session_id).slice(0, 8) : "";
    var stg = e.stage ? " stage=" + e.stage : "";
    return (
      "[" +
      e.id +
      "] " +
      e.ts +
      " " +
      String(e.level || "info").toUpperCase() +
      " " +
      e.source +
      " | " +
      e.message +
      job +
      sess +
      stg +
      det
    );
  }

  function apiErrorDetail(data, fallback) {
    if (!data || data.detail === undefined || data.detail === null) {
      return fallback || "Request failed";
    }
    var det = data.detail;
    if (Array.isArray(det)) {
      return det
        .map(function (x) {
          return x.msg || JSON.stringify(x);
        })
        .join("; ");
    }
    return String(det);
  }

  global.Ventauri = global.Ventauri || {};
  global.Ventauri.formatActivityEvent = formatActivityEvent;
  global.Ventauri.apiErrorDetail = apiErrorDetail;
})(typeof window !== "undefined" ? window : globalThis);
