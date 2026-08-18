// ==================== 生理信号参考范围与异常判定 ====================
// 各组件重复出现的「正常范围判断 / 中文标签 / 计量单位」统一收口于此。

/** 每次测量项目的正常参考区间 */
export const REF_RANGE = {
  heartRate: [60, 100],
  sbp: [90, 140],
  dbp: [60, 90],
  spo2: [95, 100],
  temp: [36.0, 37.4],
};

/** 信号字段键列表 */
export const SIGNAL_KEYS = Object.keys(REF_RANGE);

/** 中文标签映射 */
export const SIGNAL_LABELS = {
  heartRate: '心率',
  sbp: '收缩压',
  dbp: '舒张压',
  spo2: '血氧',
  temp: '体温',
};

/** 计量单位映射 */
export const SIGNAL_UNITS = {
  heartRate: 'bpm',
  sbp: 'mmHg',
  dbp: 'mmHg',
  spo2: '%',
  temp: '℃',
};

/** 判断某项生理信号是否处于正常范围 */
export function isNormal(key, v) {
  const [lo, hi] = REF_RANGE[key];
  return v >= lo && v <= hi;
}

/** 判断一条信号记录是否存在任意一项异常 */
export function rowAbnormal(r) {
  return (
    !isNormal('heartRate', r.heartRate) ||
    !isNormal('sbp', r.sbp) ||
    !isNormal('dbp', r.dbp) ||
    !isNormal('spo2', r.spo2) ||
    !isNormal('temp', r.temp)
  );
}
