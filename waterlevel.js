/**
 * Waterlevel codec - reports water level via leak sensor and triggers alarm
 * when a certain level is exceeded.
 */

"use strict";

module.exports = {
  init: function ({ log, config, publish, notify }) {
    if (!config.waterlevelCodec) {
      log.warn("Add waterlevelCodec object to configuration");
    }
    let waterlevelConfig = {
      batteryLimits: {
        min: 1.8,
        max: 4.5,
        ...config.waterlevelCodec?.batteryLimits,
      },
      waterLimits: {
        min: 40,
        max: 10,
        ...config.waterlevelCodec?.waterLimits,
      },
      leakLevel:
        config.waterlevelCodec?.leakLevel === undefined
          ? 90
          : config.waterlevelCodec.leakLevel,
      leakDebounce:
        config.waterlevelCodec?.leakDebounce === undefined
          ? 5
          : config.waterlevelCodec.leakDebounce,
      maxOfflineMinutes:
        config.waterlevelCodec?.maxOfflineMinutes === undefined
          ? 2.5 * 60
          : config.waterlevelCodec.maxOfflineMinutes,
    };
    let onlineTimeout;
    let leakState = false;
    return {
      properties: {
        batteryLevel: {
          decode: function (message) {
            const { min, max } = waterlevelConfig.batteryLimits;
            return percent(JSON.parse(message).batteryVoltage, min, max);
          },
        },
        leakDetected: {
          decode: function (message) {
            const { min, max } = waterlevelConfig.waterLimits;
            const currentLevel = percent(
              JSON.parse(message).distance,
              min,
              max
            );
            const leakLevel = waterlevelConfig.leakLevel;
            const debounce = waterlevelConfig.leakDebounce;
            if (leakState && currentLevel < leakLevel - debounce) {
              leakState = false;
            }
            if (currentLevel > leakLevel) {
              leakState = true;
            }
            return leakState;
          },
        },
        waterLevel: {
          decode: function (message) {
            const { min, max } = waterlevelConfig.waterLimits;
            return percent(JSON.parse(message).distance, min, max);
          },
        },
        online: {
          decode: function (message, info, output) {
            if (onlineTimeout !== undefined) {
              clearTimeout(onlineTimeout);
            }
            // when no message was received for `maxOfflineMinutes` set offline
            const limit = waterlevelConfig.maxOfflineMinutes * 60 * 1000;
            onlineTimeout = setTimeout(output.bind(null, "false"), limit);

            // when received message is older than `maxOfflineMinutes` set offline
            return new Date() - new Date(JSON.parse(message).timestamp) < limit
              ? "true"
              : "false";
          },
        },
        // enviroment sensor values
        currentTemperature: {
          decode: (message) => JSON.parse(message).temperature,
        },
        currentRelativeHumidity: {
          decode: (message) => JSON.parse(message).humidity,
        },
        airPressure: {
          decode: (message) => JSON.parse(message).pressure / 100,
        },
      },
    };
  },
};

let percent = (v, min, max) =>
  Math.min(100, Math.max(0, ((v - min) / (max - min)) * 100));
