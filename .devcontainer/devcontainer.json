<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="X-UA-Compatible " content="IE=edge" />
  <meta name="viewport"
    content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>在线咨询</title>
  <style>
    html,
    body {
      width: 100%;
      height: 100%;
      margin: 0;
      padding: 0
    }
  </style>
</head>
<body>
  <script type="text/javascript">
    function parse(query) {
      var qs = {};
      var i = query.indexOf('?');
      if (i < 0 && query.indexOf('=') < 0) {
        return qs;
      } else if (i >= 0) {
        query = query.substring(i + 1);
      }
      var parts = query.split('&');
      for (var n = 0; n < parts.length; n++) {
        var part = parts[n];
        var key = part.split('=')[0];
        var val = part.split('=')[1];
        key = key.toLowerCase();
        if (typeof qs[key] === 'undefined') {
          qs[key] = decodeURIComponent(val);
        } else if (typeof qs[key] === 'string') {
          var arr = [qs[key], decodeURIComponent(val)];
          qs[key] = arr;
        } else {
          qs[key].push(decodeURIComponent(val));
        }
      }
      return qs;
    }
    function init() {
      (function (m, ei, q, i, a, j, s) {
        m[i] =
          m[i] ||
          function () {
            (m[i].a = m[i].a || []).push(arguments);
          };
        (j = ei.createElement(q)), (s = ei.getElementsByTagName(q)[0]);
        j.async = true;
        j.charset = 'UTF-8';
        j.src = 'https://static.meiqia.com/widget/loader.js';
        s.parentNode.insertBefore(j, s);
      })(window, document, 'script', '_MEIQIA');
      var data = parse(window.location.search);
      var entId = data.entid || data.eid;
      if (Object.prototype.toString.call(entId) === '[object Array]') {
        entId = +entId[0];
      } else {
        entId = +entId;
      }
      _MEIQIA('entId', 'bc872db55575a28546e09b791a6e92f7' || entId);
      _MEIQIA('standalone', function (config) {
        if (config.color) {
          document.body.style['background-color'] = '#' + config.color;
        }
        if (config.url) {
          document.body.style['background-image'] = 'url(' + config.url + ')';
          document.body.style['background-repeat'] = 'no-repeat';
          document.body.style['background-size'] = '100% 100%';
        }
      });
      _MEIQIA('withoutBtn');
      if (data.metadata) {
        try {
          var metadata = JSON.parse(data.metadata);
          _MEIQIA('metadata', metadata);
        } catch (e) { }
      }
      if (data.encryptedmetadata) {
        _MEIQIA('encryptedmetadata', data.encryptedmetadata);
      }
      if (data.requestperms) {
        localStorage.setItem('requestperms', data.requestperms);
      }
      if (data.language) {
        if (data.languagelocal !== 'true') {
          _MEIQIA('language', data.language);
        }
      }
      if (data.languagelocal === 'true') {
        _MEIQIA('languageLocal', true);
      }
      if (data.subsource) {
        _MEIQIA('subSource', data.subsource);
      }
      if (data.fallback) {
        _MEIQIA('fallback', +data.fallback);
      }
      if (data.clientid) {
        _MEIQIA('clientId', data.clientid);
      }
      if (data.agentid || data.groupid) {
        _MEIQIA('assign', { agentToken: data.agentid || null, groupToken: data.groupid || null });
      }
      _MEIQIA('showPanel', {
        greeting: data.greeting || '',
        agentToken: data.agentid || null,
        groupToken: data.groupid || null
      });
    }
    init();
    </script>
    </body >
  </html >
