(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else {
		var a = factory();
		for(var i in a) (typeof exports === 'object' ? exports : root)[i] = a[i];
	}
})(global, () => {
return /******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "electron":
/*!***************************!*\
  !*** external "electron" ***!
  \***************************/
/***/ ((module) => {

module.exports = require("electron");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry needs to be wrapped in an IIFE because it needs to be isolated against other modules in the chunk.
(() => {
/*!*************************!*\
  !*** ./main/preload.ts ***!
  \*************************/
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var electron__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! electron */ "electron");
/* harmony import */ var electron__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(electron__WEBPACK_IMPORTED_MODULE_0__);

const handler = {
  send(channel, value) {
    electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.send(channel, value);
  },
  on(channel, callback) {
    const subscription = (_event, ...args) => callback(...args);
    electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.on(channel, subscription);
    return () => {
      electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.removeListener(channel, subscription);
    };
  }
};
electron__WEBPACK_IMPORTED_MODULE_0__.contextBridge.exposeInMainWorld('ipc', handler);

// Expose Electron APIs to renderer
electron__WEBPACK_IMPORTED_MODULE_0__.contextBridge.exposeInMainWorld('electron', {
  // OAuth
  openGitHubOAuth: () => electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.invoke('github-oauth'),
  exchangeCode: code => electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.invoke('exchange-code', code),
  // Auth management
  getAuth: () => electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.invoke('get-auth'),
  logout: () => electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.invoke('logout'),
  checkAuth: () => electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.invoke('check-auth'),
  // File system access
  openFolder: folderPath => electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.invoke('open-folder', folderPath),
  openExternal: url => electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.invoke('open-external', url),
  // Auth status listener
  onAuthCallback: callback => {
    electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.on('auth-callback', (_event, data) => callback(data));
  },
  onAuthStatus: callback => {
    electron__WEBPACK_IMPORTED_MODULE_0__.ipcRenderer.on('auth-status', (_event, data) => callback(data));
  }
});
})();

/******/ 	return __webpack_exports__;
/******/ })()
;
});
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoicHJlbG9hZC5qcyIsIm1hcHBpbmdzIjoiQUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSxDQUFDO0FBQ0QsTzs7Ozs7Ozs7OztBQ1ZBLHFDOzs7Ozs7VUNBQTtVQUNBOztVQUVBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7VUFDQTtVQUNBO1VBQ0E7VUFDQTtVQUNBOztVQUVBO1VBQ0E7O1VBRUE7VUFDQTtVQUNBOzs7OztXQ3RCQTtXQUNBO1dBQ0E7V0FDQTtXQUNBO1dBQ0EsaUNBQWlDLFdBQVc7V0FDNUM7V0FDQSxFOzs7OztXQ1BBO1dBQ0E7V0FDQTtXQUNBO1dBQ0EseUNBQXlDLHdDQUF3QztXQUNqRjtXQUNBO1dBQ0EsRTs7Ozs7V0NQQSx3Rjs7Ozs7V0NBQTtXQUNBO1dBQ0E7V0FDQSx1REFBdUQsaUJBQWlCO1dBQ3hFO1dBQ0EsZ0RBQWdELGFBQWE7V0FDN0QsRTs7Ozs7Ozs7Ozs7OztBQ051RTtBQUV2RSxNQUFNRSxPQUFPLEdBQUc7RUFDZEMsSUFBSUEsQ0FBQ0MsT0FBZSxFQUFFQyxLQUFjLEVBQUU7SUFDcENKLGlEQUFXLENBQUNFLElBQUksQ0FBQ0MsT0FBTyxFQUFFQyxLQUFLLENBQUM7RUFDbEMsQ0FBQztFQUNEQyxFQUFFQSxDQUFDRixPQUFlLEVBQUVHLFFBQXNDLEVBQUU7SUFDMUQsTUFBTUMsWUFBWSxHQUFHQSxDQUFDQyxNQUF3QixFQUFFLEdBQUdDLElBQWUsS0FDaEVILFFBQVEsQ0FBQyxHQUFHRyxJQUFJLENBQUM7SUFDbkJULGlEQUFXLENBQUNLLEVBQUUsQ0FBQ0YsT0FBTyxFQUFFSSxZQUFZLENBQUM7SUFFckMsT0FBTyxNQUFNO01BQ1hQLGlEQUFXLENBQUNVLGNBQWMsQ0FBQ1AsT0FBTyxFQUFFSSxZQUFZLENBQUM7SUFDbkQsQ0FBQztFQUNIO0FBQ0YsQ0FBQztBQUVEUixtREFBYSxDQUFDWSxpQkFBaUIsQ0FBQyxLQUFLLEVBQUVWLE9BQU8sQ0FBQzs7QUFFL0M7QUFDQUYsbURBQWEsQ0FBQ1ksaUJBQWlCLENBQUMsVUFBVSxFQUFFO0VBQzFDO0VBQ0FDLGVBQWUsRUFBRUEsQ0FBQSxLQUFNWixpREFBVyxDQUFDYSxNQUFNLENBQUMsY0FBYyxDQUFDO0VBQ3pEQyxZQUFZLEVBQUdDLElBQVksSUFBS2YsaURBQVcsQ0FBQ2EsTUFBTSxDQUFDLGVBQWUsRUFBRUUsSUFBSSxDQUFDO0VBRXpFO0VBQ0FDLE9BQU8sRUFBRUEsQ0FBQSxLQUFNaEIsaURBQVcsQ0FBQ2EsTUFBTSxDQUFDLFVBQVUsQ0FBQztFQUM3Q0ksTUFBTSxFQUFFQSxDQUFBLEtBQU1qQixpREFBVyxDQUFDYSxNQUFNLENBQUMsUUFBUSxDQUFDO0VBQzFDSyxTQUFTLEVBQUVBLENBQUEsS0FBTWxCLGlEQUFXLENBQUNhLE1BQU0sQ0FBQyxZQUFZLENBQUM7RUFFakQ7RUFDQU0sVUFBVSxFQUFHQyxVQUFrQixJQUFLcEIsaURBQVcsQ0FBQ2EsTUFBTSxDQUFDLGFBQWEsRUFBRU8sVUFBVSxDQUFDO0VBQ2pGQyxZQUFZLEVBQUdDLEdBQVcsSUFBS3RCLGlEQUFXLENBQUNhLE1BQU0sQ0FBQyxlQUFlLEVBQUVTLEdBQUcsQ0FBQztFQUV2RTtFQUNBQyxjQUFjLEVBQUdqQixRQUEwQyxJQUFLO0lBQzlETixpREFBVyxDQUFDSyxFQUFFLENBQUMsZUFBZSxFQUFFLENBQUNHLE1BQU0sRUFBRWdCLElBQUksS0FBS2xCLFFBQVEsQ0FBQ2tCLElBQUksQ0FBQyxDQUFDO0VBQ25FLENBQUM7RUFDREMsWUFBWSxFQUFHbkIsUUFBc0QsSUFBSztJQUN4RU4saURBQVcsQ0FBQ0ssRUFBRSxDQUFDLGFBQWEsRUFBRSxDQUFDRyxNQUFNLEVBQUVnQixJQUFJLEtBQUtsQixRQUFRLENBQUNrQixJQUFJLENBQUMsQ0FBQztFQUNqRTtBQUNGLENBQUMsQ0FBQyxDIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vbXktbmV4dHJvbi1hcHAvd2VicGFjay91bml2ZXJzYWxNb2R1bGVEZWZpbml0aW9uIiwid2VicGFjazovL215LW5leHRyb24tYXBwL2V4dGVybmFsIG5vZGUtY29tbW9uanMgXCJlbGVjdHJvblwiIiwid2VicGFjazovL215LW5leHRyb24tYXBwL3dlYnBhY2svYm9vdHN0cmFwIiwid2VicGFjazovL215LW5leHRyb24tYXBwL3dlYnBhY2svcnVudGltZS9jb21wYXQgZ2V0IGRlZmF1bHQgZXhwb3J0Iiwid2VicGFjazovL215LW5leHRyb24tYXBwL3dlYnBhY2svcnVudGltZS9kZWZpbmUgcHJvcGVydHkgZ2V0dGVycyIsIndlYnBhY2s6Ly9teS1uZXh0cm9uLWFwcC93ZWJwYWNrL3J1bnRpbWUvaGFzT3duUHJvcGVydHkgc2hvcnRoYW5kIiwid2VicGFjazovL215LW5leHRyb24tYXBwL3dlYnBhY2svcnVudGltZS9tYWtlIG5hbWVzcGFjZSBvYmplY3QiLCJ3ZWJwYWNrOi8vbXktbmV4dHJvbi1hcHAvLi9tYWluL3ByZWxvYWQudHMiXSwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIHdlYnBhY2tVbml2ZXJzYWxNb2R1bGVEZWZpbml0aW9uKHJvb3QsIGZhY3RvcnkpIHtcblx0aWYodHlwZW9mIGV4cG9ydHMgPT09ICdvYmplY3QnICYmIHR5cGVvZiBtb2R1bGUgPT09ICdvYmplY3QnKVxuXHRcdG1vZHVsZS5leHBvcnRzID0gZmFjdG9yeSgpO1xuXHRlbHNlIGlmKHR5cGVvZiBkZWZpbmUgPT09ICdmdW5jdGlvbicgJiYgZGVmaW5lLmFtZClcblx0XHRkZWZpbmUoW10sIGZhY3RvcnkpO1xuXHRlbHNlIHtcblx0XHR2YXIgYSA9IGZhY3RvcnkoKTtcblx0XHRmb3IodmFyIGkgaW4gYSkgKHR5cGVvZiBleHBvcnRzID09PSAnb2JqZWN0JyA/IGV4cG9ydHMgOiByb290KVtpXSA9IGFbaV07XG5cdH1cbn0pKGdsb2JhbCwgKCkgPT4ge1xucmV0dXJuICIsIm1vZHVsZS5leHBvcnRzID0gcmVxdWlyZShcImVsZWN0cm9uXCIpOyIsIi8vIFRoZSBtb2R1bGUgY2FjaGVcbnZhciBfX3dlYnBhY2tfbW9kdWxlX2NhY2hlX18gPSB7fTtcblxuLy8gVGhlIHJlcXVpcmUgZnVuY3Rpb25cbmZ1bmN0aW9uIF9fd2VicGFja19yZXF1aXJlX18obW9kdWxlSWQpIHtcblx0Ly8gQ2hlY2sgaWYgbW9kdWxlIGlzIGluIGNhY2hlXG5cdHZhciBjYWNoZWRNb2R1bGUgPSBfX3dlYnBhY2tfbW9kdWxlX2NhY2hlX19bbW9kdWxlSWRdO1xuXHRpZiAoY2FjaGVkTW9kdWxlICE9PSB1bmRlZmluZWQpIHtcblx0XHRyZXR1cm4gY2FjaGVkTW9kdWxlLmV4cG9ydHM7XG5cdH1cblx0Ly8gQ3JlYXRlIGEgbmV3IG1vZHVsZSAoYW5kIHB1dCBpdCBpbnRvIHRoZSBjYWNoZSlcblx0dmFyIG1vZHVsZSA9IF9fd2VicGFja19tb2R1bGVfY2FjaGVfX1ttb2R1bGVJZF0gPSB7XG5cdFx0Ly8gbm8gbW9kdWxlLmlkIG5lZWRlZFxuXHRcdC8vIG5vIG1vZHVsZS5sb2FkZWQgbmVlZGVkXG5cdFx0ZXhwb3J0czoge31cblx0fTtcblxuXHQvLyBFeGVjdXRlIHRoZSBtb2R1bGUgZnVuY3Rpb25cblx0X193ZWJwYWNrX21vZHVsZXNfX1ttb2R1bGVJZF0obW9kdWxlLCBtb2R1bGUuZXhwb3J0cywgX193ZWJwYWNrX3JlcXVpcmVfXyk7XG5cblx0Ly8gUmV0dXJuIHRoZSBleHBvcnRzIG9mIHRoZSBtb2R1bGVcblx0cmV0dXJuIG1vZHVsZS5leHBvcnRzO1xufVxuXG4iLCIvLyBnZXREZWZhdWx0RXhwb3J0IGZ1bmN0aW9uIGZvciBjb21wYXRpYmlsaXR5IHdpdGggbm9uLWhhcm1vbnkgbW9kdWxlc1xuX193ZWJwYWNrX3JlcXVpcmVfXy5uID0gKG1vZHVsZSkgPT4ge1xuXHR2YXIgZ2V0dGVyID0gbW9kdWxlICYmIG1vZHVsZS5fX2VzTW9kdWxlID9cblx0XHQoKSA9PiAobW9kdWxlWydkZWZhdWx0J10pIDpcblx0XHQoKSA9PiAobW9kdWxlKTtcblx0X193ZWJwYWNrX3JlcXVpcmVfXy5kKGdldHRlciwgeyBhOiBnZXR0ZXIgfSk7XG5cdHJldHVybiBnZXR0ZXI7XG59OyIsIi8vIGRlZmluZSBnZXR0ZXIgZnVuY3Rpb25zIGZvciBoYXJtb255IGV4cG9ydHNcbl9fd2VicGFja19yZXF1aXJlX18uZCA9IChleHBvcnRzLCBkZWZpbml0aW9uKSA9PiB7XG5cdGZvcih2YXIga2V5IGluIGRlZmluaXRpb24pIHtcblx0XHRpZihfX3dlYnBhY2tfcmVxdWlyZV9fLm8oZGVmaW5pdGlvbiwga2V5KSAmJiAhX193ZWJwYWNrX3JlcXVpcmVfXy5vKGV4cG9ydHMsIGtleSkpIHtcblx0XHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBrZXksIHsgZW51bWVyYWJsZTogdHJ1ZSwgZ2V0OiBkZWZpbml0aW9uW2tleV0gfSk7XG5cdFx0fVxuXHR9XG59OyIsIl9fd2VicGFja19yZXF1aXJlX18ubyA9IChvYmosIHByb3ApID0+IChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwob2JqLCBwcm9wKSkiLCIvLyBkZWZpbmUgX19lc01vZHVsZSBvbiBleHBvcnRzXG5fX3dlYnBhY2tfcmVxdWlyZV9fLnIgPSAoZXhwb3J0cykgPT4ge1xuXHRpZih0eXBlb2YgU3ltYm9sICE9PSAndW5kZWZpbmVkJyAmJiBTeW1ib2wudG9TdHJpbmdUYWcpIHtcblx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgU3ltYm9sLnRvU3RyaW5nVGFnLCB7IHZhbHVlOiAnTW9kdWxlJyB9KTtcblx0fVxuXHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgJ19fZXNNb2R1bGUnLCB7IHZhbHVlOiB0cnVlIH0pO1xufTsiLCJpbXBvcnQgeyBjb250ZXh0QnJpZGdlLCBpcGNSZW5kZXJlciwgSXBjUmVuZGVyZXJFdmVudCB9IGZyb20gJ2VsZWN0cm9uJ1xuXG5jb25zdCBoYW5kbGVyID0ge1xuICBzZW5kKGNoYW5uZWw6IHN0cmluZywgdmFsdWU6IHVua25vd24pIHtcbiAgICBpcGNSZW5kZXJlci5zZW5kKGNoYW5uZWwsIHZhbHVlKVxuICB9LFxuICBvbihjaGFubmVsOiBzdHJpbmcsIGNhbGxiYWNrOiAoLi4uYXJnczogdW5rbm93bltdKSA9PiB2b2lkKSB7XG4gICAgY29uc3Qgc3Vic2NyaXB0aW9uID0gKF9ldmVudDogSXBjUmVuZGVyZXJFdmVudCwgLi4uYXJnczogdW5rbm93bltdKSA9PlxuICAgICAgY2FsbGJhY2soLi4uYXJncylcbiAgICBpcGNSZW5kZXJlci5vbihjaGFubmVsLCBzdWJzY3JpcHRpb24pXG5cbiAgICByZXR1cm4gKCkgPT4ge1xuICAgICAgaXBjUmVuZGVyZXIucmVtb3ZlTGlzdGVuZXIoY2hhbm5lbCwgc3Vic2NyaXB0aW9uKVxuICAgIH1cbiAgfVxufVxuXG5jb250ZXh0QnJpZGdlLmV4cG9zZUluTWFpbldvcmxkKCdpcGMnLCBoYW5kbGVyKVxuXG4vLyBFeHBvc2UgRWxlY3Ryb24gQVBJcyB0byByZW5kZXJlclxuY29udGV4dEJyaWRnZS5leHBvc2VJbk1haW5Xb3JsZCgnZWxlY3Ryb24nLCB7XG4gIC8vIE9BdXRoXG4gIG9wZW5HaXRIdWJPQXV0aDogKCkgPT4gaXBjUmVuZGVyZXIuaW52b2tlKCdnaXRodWItb2F1dGgnKSxcbiAgZXhjaGFuZ2VDb2RlOiAoY29kZTogc3RyaW5nKSA9PiBpcGNSZW5kZXJlci5pbnZva2UoJ2V4Y2hhbmdlLWNvZGUnLCBjb2RlKSxcbiAgXG4gIC8vIEF1dGggbWFuYWdlbWVudFxuICBnZXRBdXRoOiAoKSA9PiBpcGNSZW5kZXJlci5pbnZva2UoJ2dldC1hdXRoJyksXG4gIGxvZ291dDogKCkgPT4gaXBjUmVuZGVyZXIuaW52b2tlKCdsb2dvdXQnKSxcbiAgY2hlY2tBdXRoOiAoKSA9PiBpcGNSZW5kZXJlci5pbnZva2UoJ2NoZWNrLWF1dGgnKSxcbiAgXG4gIC8vIEZpbGUgc3lzdGVtIGFjY2Vzc1xuICBvcGVuRm9sZGVyOiAoZm9sZGVyUGF0aDogc3RyaW5nKSA9PiBpcGNSZW5kZXJlci5pbnZva2UoJ29wZW4tZm9sZGVyJywgZm9sZGVyUGF0aCksXG4gIG9wZW5FeHRlcm5hbDogKHVybDogc3RyaW5nKSA9PiBpcGNSZW5kZXJlci5pbnZva2UoJ29wZW4tZXh0ZXJuYWwnLCB1cmwpLFxuICBcbiAgLy8gQXV0aCBzdGF0dXMgbGlzdGVuZXJcbiAgb25BdXRoQ2FsbGJhY2s6IChjYWxsYmFjazogKGRhdGE6IHsgY29kZTogc3RyaW5nIH0pID0+IHZvaWQpID0+IHtcbiAgICBpcGNSZW5kZXJlci5vbignYXV0aC1jYWxsYmFjaycsIChfZXZlbnQsIGRhdGEpID0+IGNhbGxiYWNrKGRhdGEpKVxuICB9LFxuICBvbkF1dGhTdGF0dXM6IChjYWxsYmFjazogKGRhdGE6IHsgaXNBdXRoZW50aWNhdGVkOiBib29sZWFuIH0pID0+IHZvaWQpID0+IHtcbiAgICBpcGNSZW5kZXJlci5vbignYXV0aC1zdGF0dXMnLCAoX2V2ZW50LCBkYXRhKSA9PiBjYWxsYmFjayhkYXRhKSlcbiAgfSxcbn0pXG5cbmV4cG9ydCB0eXBlIElwY0hhbmRsZXIgPSB0eXBlb2YgaGFuZGxlclxuIl0sIm5hbWVzIjpbImNvbnRleHRCcmlkZ2UiLCJpcGNSZW5kZXJlciIsImhhbmRsZXIiLCJzZW5kIiwiY2hhbm5lbCIsInZhbHVlIiwib24iLCJjYWxsYmFjayIsInN1YnNjcmlwdGlvbiIsIl9ldmVudCIsImFyZ3MiLCJyZW1vdmVMaXN0ZW5lciIsImV4cG9zZUluTWFpbldvcmxkIiwib3BlbkdpdEh1Yk9BdXRoIiwiaW52b2tlIiwiZXhjaGFuZ2VDb2RlIiwiY29kZSIsImdldEF1dGgiLCJsb2dvdXQiLCJjaGVja0F1dGgiLCJvcGVuRm9sZGVyIiwiZm9sZGVyUGF0aCIsIm9wZW5FeHRlcm5hbCIsInVybCIsIm9uQXV0aENhbGxiYWNrIiwiZGF0YSIsIm9uQXV0aFN0YXR1cyJdLCJzb3VyY2VSb290IjoiIn0=