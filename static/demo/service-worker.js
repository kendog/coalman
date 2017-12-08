"use strict";function setOfCachedUrls(e){return e.keys().then(function(e){return e.map(function(e){return e.url})}).then(function(e){return new Set(e)})}var precacheConfig=[["/static/demo/index.html","5f38a55b98f4e3c135bf3184e93f11e5"],["/static/demo/static/css/main.2e71cd06.css","1e306dc11a7578be60f11619a632bace"],["/static/demo/static/js/main.e5127f73.js","1058969442fc3f0ddb1af82fda41b864"],["/static/demo/static/media/Antenna-ExtraLight.2851dde4.ttf","2851dde4483b77c5ddb97ab4055d06db"],["/static/demo/static/media/Antenna-ExtraLight.6e18c2f1.woff","6e18c2f1730da3bcd021ed09c9c047f4"],["/static/demo/static/media/Antenna-ExtraLight.8a803fd5.svg","8a803fd57dfa37ed0ea99a17a839c561"],["/static/demo/static/media/Antenna-ExtraLight.9118814c.eot","9118814ccbeb5f56a3f08cbebc2bce03"],["/static/demo/static/media/Antenna-Light.18f362d3.woff","18f362d39c9c15a8c185bd2e6ae6d403"],["/static/demo/static/media/Antenna-Light.747e5a59.ttf","747e5a59f7a714034ef210177d829c75"],["/static/demo/static/media/Antenna-Light.c3e0222d.svg","c3e0222dad1df2cb75498d37bad8519f"],["/static/demo/static/media/Antenna-Light.d1eec5eb.eot","d1eec5eb57ca5b728b30feb48d6f7fee"],["/static/demo/static/media/Antenna-Regular.3a96bc31.svg","3a96bc31f874b121c2289ea2381980bc"],["/static/demo/static/media/Antenna-Regular.4ee1ebc9.woff","4ee1ebc941a7db8e65777d7f9758097c"],["/static/demo/static/media/Antenna-Regular.6cf3ecd5.ttf","6cf3ecd59bafe9bc3e0c98f64b23339b"],["/static/demo/static/media/Antenna-Regular.82a313d0.eot","82a313d017dba1a4fcc72b7cd4e781cc"],["/static/demo/static/media/region-bg-americas.c2a27581.png","c2a27581928f81782baf9f54a5f69408"],["/static/demo/static/media/region-bg-apac.565a059f.png","565a059f700bc62090ed436f46c25ecb"],["/static/demo/static/media/region-bg-emea.e8e2a5b4.png","e8e2a5b4f058fa8bc54530022c449496"]],cacheName="sw-precache-v3-sw-precache-webpack-plugin-"+(self.registration?self.registration.scope:""),ignoreUrlParametersMatching=[/^utm_/],addDirectoryIndex=function(e,t){var a=new URL(e);return"/"===a.pathname.slice(-1)&&(a.pathname+=t),a.toString()},cleanResponse=function(e){if(!e.redirected)return Promise.resolve(e);return("body"in e?Promise.resolve(e.body):e.blob()).then(function(t){return new Response(t,{headers:e.headers,status:e.status,statusText:e.statusText})})},createCacheKey=function(e,t,a,n){var c=new URL(e);return n&&c.pathname.match(n)||(c.search+=(c.search?"&":"")+encodeURIComponent(t)+"="+encodeURIComponent(a)),c.toString()},isPathWhitelisted=function(e,t){if(0===e.length)return!0;var a=new URL(t).pathname;return e.some(function(e){return a.match(e)})},stripIgnoredUrlParameters=function(e,t){var a=new URL(e);return a.hash="",a.search=a.search.slice(1).split("&").map(function(e){return e.split("=")}).filter(function(e){return t.every(function(t){return!t.test(e[0])})}).map(function(e){return e.join("=")}).join("&"),a.toString()},hashParamName="_sw-precache",urlsToCacheKeys=new Map(precacheConfig.map(function(e){var t=e[0],a=e[1],n=new URL(t,self.location),c=createCacheKey(n,hashParamName,a,/\.\w{8}\./);return[n.toString(),c]}));self.addEventListener("install",function(e){e.waitUntil(caches.open(cacheName).then(function(e){return setOfCachedUrls(e).then(function(t){return Promise.all(Array.from(urlsToCacheKeys.values()).map(function(a){if(!t.has(a)){var n=new Request(a,{credentials:"same-origin"});return fetch(n).then(function(t){if(!t.ok)throw new Error("Request for "+a+" returned a response with status "+t.status);return cleanResponse(t).then(function(t){return e.put(a,t)})})}}))})}).then(function(){return self.skipWaiting()}))}),self.addEventListener("activate",function(e){var t=new Set(urlsToCacheKeys.values());e.waitUntil(caches.open(cacheName).then(function(e){return e.keys().then(function(a){return Promise.all(a.map(function(a){if(!t.has(a.url))return e.delete(a)}))})}).then(function(){return self.clients.claim()}))}),self.addEventListener("fetch",function(e){if("GET"===e.request.method){var t,a=stripIgnoredUrlParameters(e.request.url,ignoreUrlParametersMatching),n="index.html";(t=urlsToCacheKeys.has(a))||(a=addDirectoryIndex(a,n),t=urlsToCacheKeys.has(a));var c="/static/demo/index.html";!t&&"navigate"===e.request.mode&&isPathWhitelisted(["^(?!\\/__).*"],e.request.url)&&(a=new URL(c,self.location).toString(),t=urlsToCacheKeys.has(a)),t&&e.respondWith(caches.open(cacheName).then(function(e){return e.match(urlsToCacheKeys.get(a)).then(function(e){if(e)return e;throw Error("The cached response that was expected is missing.")})}).catch(function(t){return console.warn('Couldn\'t serve response for "%s" from cache: %O',e.request.url,t),fetch(e.request)}))}});