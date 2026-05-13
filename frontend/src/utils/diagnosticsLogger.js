/**
 * DIAGNOSTICS LOGGER - Modo Observacional
 * 
 * Propósito: Mapear exactamente todos los requests, componentes, hooks y tiempos
 * que se ejecutan al entrar a Dashboard.
 * 
 * NO optimiza, NO cambia lógica, solo INSTRUMENTA.
 * 
 * Funciones:
 * - logComponentMount(componentName, props)
 * - logHookInit(hookName, endpoint, options)
 * - logFetch(method, url, params)
 * - logFetchComplete(method, url, duration, status, size)
 * - logStateChange(componentName, stateName, oldValue, newValue)
 * - logRender(componentName, renderReason)
 * - logDependencyChange(componentName, dependencyName, dependencies)
 * - printTimeline()
 */

class DiagnosticsLogger {
  constructor() {
    this.events = [];
    this.componentMap = new Map(); // { componentName: { mounts, hooks, fetches } }
    this.startTime = performance.now();
    this.requestMap = new Map(); // { requestId: { url, method, startTime, duration, status } }
  }

  /**
   * LOG: Componente montado
   */
  logComponentMount(componentName, props = {}) {
    const timestamp = performance.now() - this.startTime;
    const event = {
      type: 'MOUNT',
      component: componentName,
      timestamp,
      props,
    };
    this.events.push(event);

    if (!this.componentMap.has(componentName)) {
      this.componentMap.set(componentName, {
        mounts: 0,
        hooks: [],
        fetches: [],
        renders: [],
        stateChanges: [],
      });
    }
    this.componentMap.get(componentName).mounts++;

    console.log(
      `%c[MOUNT ${timestamp.toFixed(2)}ms] %c${componentName}`,
      'color: #10b981; font-weight: bold',
      'color: #10b981',
      props
    );
  }

  /**
   * LOG: Hook inicializado
   */
  logHookInit(hookName, componentName, endpoint = null, options = {}) {
    const timestamp = performance.now() - this.startTime;
    const event = {
      type: 'HOOK_INIT',
      hook: hookName,
      component: componentName,
      endpoint,
      options,
      timestamp,
    };
    this.events.push(event);

    if (this.componentMap.has(componentName)) {
      this.componentMap.get(componentName).hooks.push({
        name: hookName,
        endpoint,
        timestamp,
      });
    }

    console.log(
      `%c[HOOK  ${timestamp.toFixed(2)}ms] %c${componentName}:${hookName}%c → %c${endpoint || 'no-endpoint'}`,
      'color: #8b5cf6; font-weight: bold',
      'color: #8b5cf6',
      'color: #6b7280',
      'color: #3b82f6'
    );
  }

  /**
   * LOG: Fetch iniciado
   */
  logFetch(method, url, params = {}, componentName = 'unknown', requestId = null) {
    const timestamp = performance.now() - this.startTime;
    const event = {
      type: 'FETCH_START',
      method,
      url,
      params,
      component: componentName,
      timestamp,
      requestId,
    };
    this.events.push(event);

    if (this.componentMap.has(componentName)) {
      this.componentMap.get(componentName).fetches.push({
        url,
        method,
        startTime: timestamp,
        requestId,
      });
    }

    const paramsStr = Object.keys(params).length > 0 ? JSON.stringify(params) : '';
    console.log(
      `%c[FETCH #${requestId} ${timestamp.toFixed(2)}ms] %c${method} %c${url}%c${paramsStr}`,
      'color: #f59e0b; font-weight: bold',
      'color: #f59e0b',
      'color: #3b82f6',
      'color: #6b7280; font-size: 0.9em'
    );
  }

  /**
   * LOG: Fetch completado (respuesta recibida)
   */
  logFetchComplete(requestId, method, url, duration, status, responseSize = 0, componentName = 'unknown') {
    const timestamp = performance.now() - this.startTime;
    const event = {
      type: 'FETCH_COMPLETE',
      requestId,
      method,
      url,
      duration,
      status,
      responseSize,
      component: componentName,
      timestamp,
    };
    this.events.push(event);

    // Actualizar mapa de requests
    if (this.requestMap.has(requestId)) {
      const request = this.requestMap.get(requestId);
      request.duration = duration;
      request.status = status;
      request.responseSize = responseSize;
      request.completeTime = timestamp;
    }

    const statusColor = status >= 200 && status < 300 ? '#10b981' : status >= 400 ? '#ef4444' : '#f59e0b';
    const icon = status >= 200 && status < 300 ? '✅' : status >= 400 ? '❌' : '⚠️';

    console.log(
      `%c${icon} [RESP #${requestId} ${timestamp.toFixed(2)}ms] %c${method} %c${url}%c ${duration.toFixed(2)}ms - ${status} - ${(responseSize / 1024).toFixed(2)}KB`,
      `color: ${statusColor}; font-weight: bold`,
      `color: ${statusColor}`,
      'color: #3b82f6',
      `color: #6b7280; font-size: 0.85em`
    );
  }

  /**
   * LOG: Cambio de estado (useState)
   */
  logStateChange(componentName, stateName, oldValue, newValue) {
    const timestamp = performance.now() - this.startTime;
    const event = {
      type: 'STATE_CHANGE',
      component: componentName,
      stateName,
      oldValue,
      newValue,
      timestamp,
    };
    this.events.push(event);

    if (this.componentMap.has(componentName)) {
      this.componentMap.get(componentName).stateChanges.push({
        name: stateName,
        timestamp,
        from: oldValue,
        to: newValue,
      });
    }

    console.log(
      `%c[STATE ${timestamp.toFixed(2)}ms] %c${componentName}.${stateName}%c: %c${JSON.stringify(oldValue)}%c → %c${JSON.stringify(newValue)}`,
      'color: #ec4899; font-weight: bold',
      'color: #ec4899',
      'color: #6b7280',
      'color: #ef4444',
      'color: #6b7280',
      'color: #10b981'
    );
  }

  /**
   * LOG: Render del componente
   */
  logRender(componentName, renderReason = 'initial') {
    const timestamp = performance.now() - this.startTime;
    const event = {
      type: 'RENDER',
      component: componentName,
      reason: renderReason,
      timestamp,
    };
    this.events.push(event);

    if (this.componentMap.has(componentName)) {
      this.componentMap.get(componentName).renders.push({
        reason: renderReason,
        timestamp,
      });
    }

    console.log(
      `%c[RENDER ${timestamp.toFixed(2)}ms] %c${componentName}%c (${renderReason})`,
      'color: #06b6d4; font-weight: bold',
      'color: #06b6d4',
      'color: #6b7280; font-style: italic'
    );
  }

  /**
   * LOG: Cambio en dependencias de useEffect
   */
  logDependencyChange(componentName, effectName, dependencies) {
    const timestamp = performance.now() - this.startTime;
    const event = {
      type: 'DEPENDENCY_CHANGE',
      component: componentName,
      effect: effectName,
      dependencies,
      timestamp,
    };
    this.events.push(event);

    console.log(
      `%c[DEPS ${timestamp.toFixed(2)}ms] %c${componentName}.${effectName}`,
      'color: #a78bfa; font-weight: bold',
      'color: #a78bfa',
      dependencies
    );
  }

  /**
   * IMPRIME: Timeline visual en la consola
   */
  printTimeline() {
    console.clear();
    console.log(
      '%c═══════════════════════════════════════════════════════════════',
      'color: #3b82f6; font-weight: bold; font-size: 1.1em'
    );
    console.log(
      '%c         DASHBOARD DIAGNOSTICS - OBSERVATIONAL MODE',
      'color: #3b82f6; font-weight: bold; font-size: 1.1em'
    );
    console.log(
      '%c═══════════════════════════════════════════════════════════════',
      'color: #3b82f6; font-weight: bold; font-size: 1.1em'
    );

    // Timeline de eventos
    console.log('%c\n📊 TIMELINE DE EVENTOS:\n', 'color: #ec4899; font-weight: bold; font-size: 1.05em');

    this.events.forEach((event, idx) => {
      const prefix = `[${idx + 1}]`;
      const time = event.timestamp.toFixed(2);

      switch (event.type) {
        case 'MOUNT':
          console.log(
            `${prefix} %cMOUNT${' '.repeat(5)} %c${time}ms %c${event.component}`,
            'color: #10b981; font-weight: bold',
            'color: #6b7280',
            'color: #10b981'
          );
          break;
        case 'HOOK_INIT':
          console.log(
            `${prefix} %cHOOK${' '.repeat(6)} %c${time}ms %c${event.component}:${event.hook}%c → %c${event.endpoint || 'N/A'}`,
            'color: #8b5cf6; font-weight: bold',
            'color: #6b7280',
            'color: #8b5cf6',
            'color: #6b7280',
            'color: #3b82f6'
          );
          break;
        case 'FETCH_START':
          console.log(
            `${prefix} %c▶ FETCH%c #${event.requestId}%c ${time}ms %c${event.method}%c ${event.url}`,
            'color: #f59e0b; font-weight: bold',
            'color: #f59e0b',
            'color: #6b7280',
            'color: #f59e0b',
            'color: #3b82f6'
          );
          break;
        case 'FETCH_COMPLETE':
          const statusColor = event.status >= 200 && event.status < 300 ? '#10b981' : '#ef4444';
          console.log(
            `${prefix} %c◀ RESP${' '.repeat(2)} #${event.requestId}%c ${time}ms %c${event.duration.toFixed(2)}ms%c ${event.status}%c ${event.url}`,
            `color: ${statusColor}; font-weight: bold`,
            'color: #6b7280',
            `color: ${statusColor}`,
            `color: ${statusColor}`,
            'color: #3b82f6'
          );
          break;
        case 'STATE_CHANGE':
          console.log(
            `${prefix} %cSTATE${' '.repeat(4)} %c${time}ms %c${event.component}.${event.stateName}`,
            'color: #ec4899; font-weight: bold',
            'color: #6b7280',
            'color: #ec4899'
          );
          break;
        case 'RENDER':
          console.log(
            `${prefix} %cRENDER${' '.repeat(3)} %c${time}ms %c${event.component}%c (${event.reason})`,
            'color: #06b6d4; font-weight: bold',
            'color: #6b7280',
            'color: #06b6d4',
            'color: #6b7280; font-style: italic'
          );
          break;
        default:
          break;
      }
    });

    // Mapa de componentes
    console.log('%c\n🗺️  COMPONENT MAP:\n', 'color: #06b6d4; font-weight: bold; font-size: 1.05em');
    this.componentMap.forEach((data, componentName) => {
      console.log(
        `%c${componentName}%c`,
        'color: #06b6d4; font-weight: bold',
        'color: #6b7280'
      );
      console.log(`  Mounts: ${data.mounts}`);
      console.log(`  Hooks: ${data.hooks.length}`);
      data.hooks.forEach((h) => {
        console.log(`    - ${h.name} → ${h.endpoint || 'N/A'} (${h.timestamp.toFixed(2)}ms)`);
      });
      console.log(`  Fetches: ${data.fetches.length}`);
      data.fetches.forEach((f) => {
        console.log(`    - #${f.requestId} ${f.method} ${f.url}`);
      });
      console.log(`  State Changes: ${data.stateChanges.length}`);
      console.log(`  Renders: ${data.renders.length}`);
    });

    // Análisis de requests
    console.log('%c\n📡 REQUESTS ANALYSIS:\n', 'color: #f59e0b; font-weight: bold; font-size: 1.05em');
    const sortedRequests = Array.from(this.requestMap.values()).sort((a, b) => a.startTime - b.startTime);
    sortedRequests.forEach((req) => {
      const durationStr = req.duration ? `${req.duration.toFixed(2)}ms` : 'pending';
      const statusColor = req.status && req.status >= 200 && req.status < 300 ? '#10b981' : '#ef4444';
      const status = req.status || '?';

      console.log(
        `%c#${req.requestId}%c ${req.method} %c${req.url}%c | Duration: ${durationStr} | Status: %c${status}`,
        'color: #f59e0b; font-weight: bold',
        'color: #6b7280',
        'color: #3b82f6',
        'color: #6b7280',
        `color: ${statusColor}; font-weight: bold`
      );
    });

    // Estadísticas globales
    const totalTime = performance.now() - this.startTime;
    const fetchCount = Array.from(this.requestMap.values()).length;
    const avgFetchDuration = Array.from(this.requestMap.values())
      .filter((r) => r.duration)
      .reduce((sum, r) => sum + r.duration, 0) / Math.max(fetchCount, 1);

    console.log('%c\n📈 GLOBAL STATS:\n', 'color: #10b981; font-weight: bold; font-size: 1.05em');
    console.log(`Total Time: ${totalTime.toFixed(2)}ms`);
    console.log(`Total Requests: ${fetchCount}`);
    console.log(`Avg Request Duration: ${avgFetchDuration.toFixed(2)}ms`);
    console.log(`Total Events: ${this.events.length}`);

    console.log(
      '%c\n═══════════════════════════════════════════════════════════════',
      'color: #3b82f6; font-weight: bold; font-size: 1.1em'
    );
  }

  /**
   * Exportar datos de diagnóstico como JSON
   */
  exportDiagnostics() {
    return {
      timestamp: new Date().toISOString(),
      totalTime: performance.now() - this.startTime,
      events: this.events,
      componentMap: Object.fromEntries(this.componentMap),
      requests: Array.from(this.requestMap.entries()).map(([id, data]) => ({
        id,
        ...data,
      })),
    };
  }

  /**
   * Registrar un request en el mapa de requests
   */
  registerRequest(requestId, method, url, startTime) {
    this.requestMap.set(requestId, {
      requestId,
      method,
      url,
      startTime,
      duration: null,
      status: null,
      responseSize: 0,
    });
  }
}

// Singleton instance
export const diagnostics = new DiagnosticsLogger();

// Export para uso en componentes
export default diagnostics;
