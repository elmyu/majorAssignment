<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { getDevices, createDevice, updateDevice, deleteDevice } from '@/services/api.js'
import { RUN_STATUSES, RUN_STATUS_CLASS, USE_STATUSES, DEPARTMENTS } from '@/utils/constants.js'
import { fmtPrice } from '@/utils/format.js'

const devices = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const showBatchConfirm = ref(false)
const showBatchAdd = ref(false)
const editingDevice = ref(null)
const deleteTarget = ref(null)
const toasts = ref([])
const selectedIds = ref(new Set())

// 拖拽框选
const tableWrap = ref(null)
const dragStart = ref(null)
const isDragging = ref(false)
const dragRect = ref(null)

const form = reactive({ name: '', model: '', department: '', purchaseDate: '', price: null, status: '正常使用', runStatus: '在线', note: '' })
const batchRows = ref([])
const departmentOptions = DEPARTMENTS
const runStatusOptions = RUN_STATUSES

const activeCount = computed(() => devices.value.filter(d => d.status === '正常使用').length)
const repairCount = computed(() => devices.value.filter(d => d.status === '维修中').length)
const idleCount = computed(() => devices.value.filter(d => d.status === '闲置').length)
const scrappedCount = computed(() => devices.value.filter(d => d.status === '已报废').length)

const filteredDevices = computed(() => {
  let r = devices.value
  const q = searchQuery.value.trim().toLowerCase()
  if (q) r = r.filter(d => [d.name, d.model, d.department, d.code, d.note].some(x => (x || '').toLowerCase().includes(q)))
  if (statusFilter.value) r = r.filter(d => d.status === statusFilter.value)
  return [...r].sort((a, b) => new Date(b.purchaseDate) - new Date(a.purchaseDate))
})

const stClass = (s) => ({ '正常使用': 'active', '维修中': 'repair', '闲置': 'idle', '已报废': 'scrapped' }[s] || 'idle')
const runClass = (r) => RUN_STATUS_CLASS[r] || 'offline'

const showToast = (m, t = 'info') => {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, message: m, type: t })
  setTimeout(() => (toasts.value = toasts.value.filter(x => x.id !== id)), 2800)
}
const setFilter = (s) => (statusFilter.value = statusFilter.value === s ? '' : s)

function loadDevices() { try { devices.value = getDevices() } catch (e) { showToast(e.message, 'warning') } }
onMounted(() => { loadDevices(); bindDrag() })
onBeforeUnmount(() => { unbindDrag() })

// ---- 拖拽框选 ----
function bindDrag() { document.addEventListener('mousemove', onDragMove); document.addEventListener('mouseup', onDragUp) }
function unbindDrag() { document.removeEventListener('mousemove', onDragMove); document.removeEventListener('mouseup', onDragUp) }
function startDrag(e) {
  if (e.target.closest('input, select, button, a, .ops')) return
  dragStart.value = { x: e.clientX, y: e.clientY }
  isDragging.value = true
  dragRect.value = null
}
function onDragMove(e) {
  if (!isDragging.value || !dragStart.value) return
  dragRect.value = { x: Math.min(dragStart.value.x, e.clientX), y: Math.min(dragStart.value.y, e.clientY), w: Math.abs(e.clientX - dragStart.value.x), h: Math.abs(e.clientY - dragStart.value.y) }
  if (!tableWrap.value) return
  const rows = tableWrap.value.querySelectorAll('.device-table tbody tr.draggable')
  rows.forEach((row) => {
    const r = row.getBoundingClientRect(); const rect = dragRect.value
    const hit = !(r.right < rect.x || r.left > rect.x + rect.w || r.bottom < rect.y || r.top > rect.y + rect.h)
    const s = new Set(selectedIds.value)
    if (hit) s.add(row.dataset.id); else s.delete(row.dataset.id)
    selectedIds.value = s
  })
}
function onDragUp() { isDragging.value = false; dragRect.value = null }
function clearSel() { selectedIds.value = new Set() }

const toggleSelect = (id) => { const s = new Set(selectedIds.value); s.has(id) ? s.delete(id) : s.add(id); selectedIds.value = s }
const isAllSelected = computed(() => filteredDevices.value.length > 0 && filteredDevices.value.every(d => selectedIds.value.has(d.id)))
const toggleSelectAll = () => {
  if (isAllSelected.value) selectedIds.value = new Set()
  else { const s = new Set(selectedIds.value); filteredDevices.value.forEach(d => s.add(d.id)); selectedIds.value = s }
}

function openAddModal() { editingDevice.value = null; Object.assign(form, { name: '', model: '', department: '', purchaseDate: new Date().toISOString().split('T')[0], price: null, status: '正常使用', runStatus: '在线', note: '' }); showModal.value = true; showBatchAdd.value = false }
function openEditModal(d) { editingDevice.value = d; Object.assign(form, { name: d.name, model: d.model, department: d.department, purchaseDate: d.purchaseDate, price: d.price, status: d.status, runStatus: d.runStatus || '在线', note: d.note || '' }); showModal.value = true; showBatchAdd.value = false }
const closeModal = () => { showModal.value = false; editingDevice.value = null; showBatchAdd.value = false }

function submitForm() {
  if (!form.name.trim()) return showToast('请输入设备名称', 'warning')
  if (!form.department) return showToast('请选择所属科室', 'warning')
  if (!form.purchaseDate) return showToast('请选择购置日期', 'warning')
  if (form.price === null || form.price === '' || form.price < 0) return showToast('请输入有效的价格', 'warning')
  const data = { name: form.name.trim(), model: form.model.trim(), department: form.department, purchaseDate: form.purchaseDate, price: Number(form.price), status: form.status, runStatus: form.runStatus, note: form.note.trim() }
  try {
    if (editingDevice.value) { updateDevice(editingDevice.value.id, data); showToast('设备信息已更新', 'success') }
    else { createDevice(data); showToast('新设备已成功录入', 'success') }
    closeModal(); loadDevices()
  } catch (e) { showToast(e.message, 'warning') }
}

// ---- 批量新增 ----
const emptyRow = () => ({ name: '', model: '', department: '', purchaseDate: new Date().toISOString().split('T')[0], price: null, status: '正常使用', runStatus: '在线', note: '' })
function openBatchAdd() { editingDevice.value = null; batchRows.value = [emptyRow()]; showBatchAdd.value = true; showModal.value = true }
function addRow() { batchRows.value.push(emptyRow()) }
function removeRow(i) { if (batchRows.value.length > 1) batchRows.value.splice(i, 1); else batchRows.value = [emptyRow()] }
function submitBatch() {
  const valid = batchRows.value.filter(r => r.name && r.department && r.purchaseDate)
  const invalid = batchRows.value.length - valid.length
  if (!valid.length) return showToast('请至少填写一台有效设备', 'warning')
  let ok = 0
  try { valid.forEach(r => { createDevice({ name: r.name.trim(), model: r.model.trim(), department: r.department, purchaseDate: r.purchaseDate, price: Number(r.price) || 0, status: r.status, runStatus: r.runStatus, note: r.note.trim() }); ok++ }) }
  catch (e) { return showToast(e.message, 'warning') }
  showToast(invalid ? `成功录入 ${ok} 台（跳过 ${invalid} 行）` : `成功批量录入 ${ok} 台设备`, 'success')
  closeModal(); loadDevices()
}

function changeStatus(d, ns) { try { updateDevice(d.id, { status: ns }); d.status = ns; showToast(`「${d.name}」已更新为"${ns}"`, 'success') } catch (e) { showToast(e.message, 'warning') } }
function changeRunStatus(d, ns) { try { updateDevice(d.id, { runStatus: ns }); d.runStatus = ns; showToast(`「${d.name}」运行状态已更新为"${ns}"`, 'success') } catch (e) { showToast(e.message, 'warning') } }

function confirmDelete(d) { deleteTarget.value = d; showDeleteConfirm.value = true }
const cancelDelete = () => { showDeleteConfirm.value = false; deleteTarget.value = null }
function executeDelete() {
  try { deleteDevice(deleteTarget.value.id); devices.value = devices.value.filter(x => x.id !== deleteTarget.value.id); showToast(`设备「${deleteTarget.value.name}」已删除`, 'success') }
  catch (e) { showToast(e.message, 'warning') }
  cancelDelete()
}
function confirmClearScrapped() {
  const count = devices.value.filter(d => d.status === '已报废').length
  if (!count) return showToast('没有可清空的报废设备', 'info')
  devices.value.filter(d => d.status === '已报废').forEach(d => { try { deleteDevice(d.id) } catch (e) {} })
  loadDevices(); showToast(`已清空 ${count} 台报废设备`, 'success')
}

const batchSelectedCount = computed(() => selectedIds.value.size)
function executeBatchDelete() {
  const ids = [...selectedIds.value]
  if (!ids.length) { showBatchConfirm.value = false; return }
  ids.forEach(id => { try { deleteDevice(id) } catch (e) {} })
  selectedIds.value = new Set(); loadDevices(); showToast(`已批量删除 ${ids.length} 台设备`, 'success'); showBatchConfirm.value = false
}
</script>

<template>
  <div class="device-manage">
    <div class="head-desc">设备物资维护：新增 / 批量录入设备，修改状态；可按住左键拖动框选多行删除。</div>

    <section class="stats-bar">
      <button class="chip" :class="{ active: statusFilter === '' }" @click="setFilter('')">全部 <b>{{ devices.length }}</b></button>
      <button class="chip" :class="{ active: statusFilter === '正常使用' }" @click="setFilter('正常使用')">正常使用 <b>{{ activeCount }}</b></button>
      <button class="chip" :class="{ active: statusFilter === '维修中' }" @click="setFilter('维修中')">维修中 <b>{{ repairCount }}</b></button>
      <button class="chip" :class="{ active: statusFilter === '闲置' }" @click="setFilter('闲置')">闲置 <b>{{ idleCount }}</b></button>
      <button class="chip chip-scrapped" :class="{ active: statusFilter === '已报废' }" @click="setFilter('已报废')">已报废 <b>{{ scrappedCount }}</b></button>
    </section>

    <section class="toolbar">
      <input v-model="searchQuery" placeholder="搜索名称 / 型号 / 科室 / 编号" class="search-input" />
      <span class="result-count">共 <b>{{ filteredDevices.length }}</b> 台</span>
      <div class="action-bar">
        <button class="btn btn-add" @click="openAddModal">新增</button>
        <button class="btn btn-add" @click="openBatchAdd">批量新增</button>
        <button class="btn btn-batch" @click="showBatchConfirm = true" :disabled="batchSelectedCount === 0">删除选中<span v-if="batchSelectedCount" class="cnt">{{ batchSelectedCount }}</span></button>
        <button class="btn btn-clear" @click="confirmClearScrapped" :disabled="scrappedCount === 0">清空报废<span v-if="scrappedCount" class="cnt">{{ scrappedCount }}</span></button>
        <button v-if="batchSelectedCount" class="btn btn-reset" @click="clearSel">取消选择</button>
      </div>
    </section>

    <section class="table-card" ref="tableWrap" @mousedown="startDrag">
      <div class="drag-hint">提示：按住左键拖动框选可一次选择多行</div>
      <table class="device-table" v-if="filteredDevices.length">
        <thead><tr>
          <th class="col-check"><input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" /></th>
          <th>编号</th><th>设备名称</th><th>所属科室</th><th>型号</th><th>购置日期</th><th>价格(元)</th>
          <th>使用状态</th><th>运行状态</th><th>备注</th><th>操作</th>
        </tr></thead>
        <tbody>
          <tr v-for="device in filteredDevices" :key="device.id" :data-id="device.id" class="draggable"
              :class="{ scrapped: device.status === '已报废', sel: selectedIds.has(device.id), fail: device.runStatus === '故障' }">
            <td class="col-check"><input type="checkbox" :checked="selectedIds.has(device.id)" @change="toggleSelect(device.id)" /></td>
            <td class="code">{{ device.code }}</td>
            <td class="name">{{ device.name }}</td>
            <td>{{ device.department }}</td>
            <td>{{ device.model || '-' }}</td>
            <td>{{ device.purchaseDate }}</td>
            <td>¥{{ fmtPrice(device.price) }}</td>
            <td><span class="badge" :class="'st-' + stClass(device.status)">{{ device.status }}</span></td>
            <td><select class="run-sel" :class="'run-' + runClass(device.runStatus)" :value="device.runStatus" @change="changeRunStatus(device, $event.target.value)">
              <option v-for="r in runStatusOptions" :key="r" :value="r">{{ r }}</option></select></td>
            <td class="note">{{ device.note || '-' }}</td>
            <td><div class="ops"><button class="op-edit" @click="openEditModal(device)">编辑</button><button class="op-del" @click="confirmDelete(device)">删除</button></div></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">{{ searchQuery || statusFilter ? '未找到匹配设备' : '暂无设备数据' }}</div>
      <div v-if="dragRect" class="drag-box" :style="{ left: dragRect.x + 'px', top: dragRect.y + 'px', width: dragRect.w + 'px', height: dragRect.h + 'px' }"></div>
    </section>

    <!-- 新增/编辑 -->
    <div v-if="showModal && !showBatchAdd" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-head"><h3>{{ editingDevice ? '编辑设备信息' : '新增医疗设备' }}</h3><button class="x" @click="closeModal">✕</button></div>
        <form class="modal-body" @submit.prevent="submitForm">
          <div class="row2">
            <label class="f">设备名称 *<input v-model="form.name" required maxlength="50" /></label>
            <label class="f">型号<input v-model="form.model" maxlength="30" /></label>
          </div>
          <div class="row2">
            <label class="f">所属科室 *<select v-model="form.department" required><option value="">请选择</option><option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option></select></label>
            <label class="f">购置日期 *<input type="date" v-model="form.purchaseDate" required /></label>
          </div>
          <div class="row2">
            <label class="f">价格(元) *<input type="number" v-model.number="form.price" min="0" step="0.01" required /></label>
            <label class="f">使用状态<select v-model="form.status"><option v-for="s in USE_STATUSES" :key="s" :value="s">{{ s }}</option></select></label>
          </div>
          <label class="f">运行状态<select v-model="form.runStatus"><option v-for="r in runStatusOptions" :key="r" :value="r">{{ r }}</option></select></label>
          <label class="f">备注<textarea v-model="form.note" maxlength="200" rows="2"></textarea></label>
          <div class="modal-foot"><button type="button" class="btn ghost" @click="closeModal">取消</button><button type="submit" class="btn pri">{{ editingDevice ? '保存修改' : '确认录入' }}</button></div>
        </form>
      </div>
    </div>

    <!-- 批量新增 -->
    <div v-if="showBatchAdd" class="modal-overlay" @click.self="closeModal">
      <div class="modal modal-batch">
        <div class="modal-head"><h3>批量新增设备（{{ batchRows.length }} 行）</h3><button class="x" @click="closeModal">✕</button></div>
        <div class="modal-body batch-body">
          <div class="batch-table">
            <div class="brow bhead"><span>设备名称*</span><span>型号</span><span>所属科室*</span><span>购置日期*</span><span>价格(元)</span><span>使用状态</span><span>备注</span></div>
            <div v-for="(row, i) in batchRows" :key="i" class="brow">
              <input v-model="row.name" placeholder="名称" />
              <input v-model="row.model" placeholder="型号" />
              <select v-model="row.department"><option value="">科室</option><option v-for="d in departmentOptions" :key="d" :value="d">{{ d }}</option></select>
              <input type="date" v-model="row.purchaseDate" />
              <input type="number" v-model.number="row.price" min="0" step="0.01" placeholder="0.00" />
              <select v-model="row.status"><option v-for="s in USE_STATUSES" :key="s" :value="s">{{ s }}</option></select>
              <input v-model="row.note" placeholder="备注" />
              <button class="row-del" type="button" @click="removeRow(i)">✕</button>
            </div>
          </div>
          <button type="button" class="btn add-row" @click="addRow">+ 添加一行</button>
        </div>
        <div class="modal-foot"><button type="button" class="btn ghost" @click="closeModal">取消</button><button type="button" class="btn pri" @click="submitBatch">批量提交</button></div>
      </div>
    </div>

    <div v-if="showDeleteConfirm" class="del-overlay" @click.self="cancelDelete">
      <div class="del-dialog"><div class="del-icon">!</div><h3 class="del-title">确认删除</h3>
        <p v-if="deleteTarget" class="del-text">确定要删除设备 <b class="del-name">{{ deleteTarget.name }}</b><br />（{{ deleteTarget.code }}）<br /><span class="del-warn">此操作不可恢复！</span></p>
        <div class="del-btns"><button class="del-cancel" @click="cancelDelete">取消</button><button class="del-confirm" @click="executeDelete">确认删除</button></div>
      </div>
    </div>

    <div v-if="showBatchConfirm" class="del-overlay" @click.self="showBatchConfirm = false">
      <div class="del-dialog"><div class="del-icon">!</div><h3 class="del-title">批量删除</h3>
        <p class="del-text">确定要批量删除选中的 <b class="del-name">{{ batchSelectedCount }}</b> 台设备吗？<br /><span class="del-warn">此操作不可恢复！</span></p>
        <div class="del-btns"><button class="del-cancel" @click="showBatchConfirm = false">取消</button><button class="del-confirm" @click="executeBatchDelete">确认删除</button></div>
      </div>
    </div>

    <div class="toast-container"><div v-for="t in toasts" :key="t.id" class="toast-item" :class="'toast-' + t.type">{{ t.message }}</div></div>
  </div>
</template>

<style scoped>
.device-manage { display: flex; flex-direction: column; gap: 14px; }
.head-desc { padding: 10px 14px; background: #eef6ee; color: #3d6b40; border: 1px solid #d0e4d0; font-size: 0.85rem; }
.stats-bar { display: flex; gap: 8px; flex-wrap: wrap; background: #fff; border: 1px solid #eef2ee; padding: 10px 12px; }
.chip { padding: 6px 14px; font-size: 0.84rem; color: #4b5563; background: #f6f8f6; border: 1px solid transparent; cursor: pointer; font-family: inherit; }
.chip b { font-weight: 700; }
.chip.active { border-color: #83b785; color: #3d6b40; }
.toolbar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.search-input { flex: 1; min-width: 220px; max-width: 360px; padding: 8px 12px; border: 1px solid #e5e7eb; font-size: 0.84rem; font-family: inherit; box-sizing: border-box; }
.result-count { font-size: 0.85rem; color: #4b5563; }
.result-count b { color: #4a854d; }
.action-bar { display: flex; gap: 8px; margin-left: auto; flex-wrap: wrap; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; font-size: 0.84rem; font-weight: 600; cursor: pointer; border: 1px solid transparent; font-family: inherit; }
.btn-add { background: #4a854d; color: #fff; } .btn-add:hover { background: #3d6b40; }
.btn-batch { background: #fff; color: #8a6d3b; border-color: #eee2c8; }
.btn-clear { background: #fff; color: #c0392b; border-color: #f0c8c8; }
.btn-reset { background: #fff; color: #6b7280; border-color: #e0e7e0; }
.btn:disabled { opacity: 0.45; cursor: not-allowed; }
.cnt { display: inline-flex; align-items: center; justify-content: center; min-width: 18px; height: 18px; padding: 0 5px; font-size: 0.68rem; font-weight: 800; background: #d03434; color: #fff; border-radius: 10px; }
.table-card { background: #fff; border: 1px solid #eef2ee; overflow-x: auto; position: relative; }
.drag-hint { padding: 8px 12px; font-size: 0.75rem; color: #93a293; border-bottom: 1px solid #f0f3f0; background: #fbfdfb; }
.device-table { width: 100%; border-collapse: collapse; min-width: 1000px; font-size: 0.82rem; }
.device-table th { padding: 10px 12px; text-align: left; background: #f2f7f2; color: #557457; border-bottom: 2px solid #b8d8b9; white-space: nowrap; }
.device-table td { padding: 9px 12px; border-bottom: 1px solid #f3f4f6; color: #4b5563; vertical-align: middle; }
.device-table tbody tr.scrapped { background: #fefafa; opacity: 0.7; }
.device-table tbody tr.sel { background: #eef6ee; }
.device-table tbody tr.fail { background: #fdecec; } .device-table tbody tr.fail:hover { background: #fbdfe0; }
.drag-box { position: fixed; background: rgba(74, 133, 77, 0.18); border: 1px solid rgba(74, 133, 77, 0.6); pointer-events: none; z-index: 5; }
.col-check { width: 40px; text-align: center; }
.code { font-family: monospace; font-size: 0.76rem; color: #6b7280; }
.name { font-weight: 600; color: #1f2937; }
.badge { display: inline-block; padding: 3px 10px; font-size: 0.72rem; font-weight: 600; }
.st-active { background: #e6f7ef; color: #2d7d4f; } .st-repair { background: #fdf3e0; color: #8b6914; } .st-idle { background: #e8f0f8; color: #3d5f80; } .st-scrapped { background: #fde8e8; color: #9b2c2c; }
.run-sel { padding: 3px 8px; font-size: 0.72rem; font-weight: 600; border: 1px solid transparent; cursor: pointer; font-family: inherit; }
.run-online { background: #e7faf1; color: #0b7d4f; } .run-running { background: #e7f1ff; color: #2563eb; } .run-fail { background: #fdecec; color: #dc2626; } .run-calib { background: #fdf5e0; color: #b45309; } .run-offline { background: #eef0f2; color: #6b7280; }
.ops { display: flex; gap: 4px; align-items: center; }
.op-edit, .op-del { padding: 4px 10px; border: 1px solid transparent; cursor: pointer; font-size: 0.76rem; font-family: inherit; }
.op-edit { background: #eef2ff; color: #5b6abf; } .op-del { background: #fde8e8; color: #c0392b; }
.note { max-width: 130px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #9ca3af; }
.empty { text-align: center; padding: 50px; color: #b0b0b0; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal { background: #fff; width: 100%; max-width: 560px; max-height: 85vh; overflow-y: auto; }
.modal-batch { max-width: 900px; }
.modal-head { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid #eef2ee; }
.modal-head h3 { margin: 0; }
.x { border: none; background: #f3f4f6; width: 28px; height: 28px; cursor: pointer; }
.modal-body { padding: 16px 18px; display: flex; flex-direction: column; gap: 12px; }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.f { display: flex; flex-direction: column; gap: 5px; font-size: 0.82rem; font-weight: 600; color: #4b5563; }
.f input, .f select, .f textarea { padding: 8px 10px; border: 1px solid #e0e7e0; font-family: inherit; font-size: 0.85rem; }
.batch-body { overflow-x: auto; }
.batch-table { min-width: 760px; }
.brow { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 0.9fr 1fr 1.2fr; gap: 6px; margin-bottom: 8px; align-items: center; }
.brow:not(.bhead) { grid-template-columns: 1.2fr 1fr 1fr 1fr 0.9fr 1fr 1.2fr 28px; }
.brow input, .brow select { padding: 7px 8px; border: 1px solid #e0e7e0; font-size: 0.8rem; font-family: inherit; }
.bhead span { font-size: 0.75rem; font-weight: 700; color: #557457; }
.row-del { border: none; background: #fde8e8; color: #c0392b; cursor: pointer; height: 30px; }
.add-row { align-self: flex-start; background: #eef6ee; color: #3d6b40; border: 1px dashed #9cc39f; }
.modal-foot { display: flex; justify-content: flex-end; gap: 10px; padding: 12px 18px; border-top: 1px solid #eef2ee; }
.btn.ghost { background: #f3f4f6; color: #6b7280; } .btn.pri { background: #4a854d; color: #fff; }
.toast-container { position: fixed; top: 20px; right: 20px; z-index: 2000; display: flex; flex-direction: column; gap: 8px; }
.toast-item { padding: 10px 16px; background: #fff; font-size: 0.84rem; border-left: 4px solid #83b785; }
.toast-success { border-left-color: #4caf84; } .toast-warning { border-left-color: #e8a840; } .toast-info { border-left-color: #5b8ec4; }
.del-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.55); display: flex; align-items: center; justify-content: center; z-index: 2000; padding: 20px; }
.del-dialog { background: #fff; width: 100%; max-width: 400px; border-radius: 10px; padding: 30px 26px; text-align: center; border: 3px solid #c0392b; box-shadow: 0 12px 50px rgba(0, 0, 0, 0.35); }
.del-icon { width: 64px; height: 64px; margin: 0 auto 14px; border-radius: 50%; background: #c0392b; color: #fff; font-size: 2.4rem; font-weight: 900; line-height: 64px; text-align: center; }
.del-title { margin: 0 0 12px; font-size: 1.4rem; color: #c0392b; font-weight: 800; }
.del-text { margin: 0 0 22px; font-size: 1rem; color: #333; line-height: 1.7; }
.del-name { color: #c0392b; font-size: 1.1rem; }
.del-warn { color: #c0392b; font-weight: 700; font-size: 0.95rem; }
.del-btns { display: flex; gap: 14px; justify-content: center; }
.del-cancel, .del-confirm { flex: 1; padding: 12px 0; border: none; border-radius: 6px; font-size: 1rem; font-weight: 700; cursor: pointer; font-family: inherit; }
.del-cancel { background: #e5e7eb; color: #4b5563; } .del-cancel:hover { background: #d1d5db; }
.del-confirm { background: #c0392b; color: #fff; } .del-confirm:hover { background: #a93226; }
@media (max-width: 640px) { .row2 { grid-template-columns: 1fr; } }
</style>
