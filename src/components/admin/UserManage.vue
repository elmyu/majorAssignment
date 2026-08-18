<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { listUsers, createUser, updateUser, deleteUser } from '@/services/api.js'
import { ROLE_LABELS } from '@/utils/constants.js'

const users = ref([])
const loading = ref(true)
const errorMsg = ref('')
const roleFilter = ref('all')
const search = ref('')

const showModal = ref(false)
const editing = ref(null)
const form = ref({})
const toast = ref('')
const confirmDel = ref(null)
const selectedIds = ref(new Set())
const confirmBatchDel = ref(false)

// 拖拽框选
const tableWrap = ref(null)
const dragStart = ref(null)
const isDragging = ref(false)
const dragRect = ref(null)

function showToast(msg, type = 'success') { toast.value = { msg, type }; setTimeout(() => (toast.value = null), 2400) }

onMounted(() => { load(); bindDrag() })
onBeforeUnmount(() => { unbindDrag() })

function load() {
  try { users.value = listUsers(roleFilter.value) } catch (e) { errorMsg.value = e.message } finally { loading.value = false }
}

// 可被选择/删除的用户（admin 除外）
const deletable = computed(() => users.value.filter(u => u.role !== 'admin'))
const displayed = computed(() => {
  return users.value.filter((u) => !search.value || u.name.includes(search.value) || u.account.includes(search.value))
})
const displayedDeletable = computed(() => displayed.value.filter(u => u.role !== 'admin'))
const batchCount = computed(() => selectedIds.value.size)

// ---- 拖拽框选 ----
function bindDrag() { document.addEventListener('mousemove', onDragMove); document.addEventListener('mouseup', onDragUp) }
function unbindDrag() { document.removeEventListener('mousemove', onDragMove); document.removeEventListener('mouseup', onDragUp) }
function startDrag(e) {
  if (e.target.closest('input, select, button, a, .ops')) return
  dragStart.value = { x: e.clientX, y: e.clientY }; isDragging.value = true; dragRect.value = null
}
function onDragMove(e) {
  if (!isDragging.value || !dragStart.value) return
  dragRect.value = { x: Math.min(dragStart.value.x, e.clientX), y: Math.min(dragStart.value.y, e.clientY), w: Math.abs(e.clientX - dragStart.value.x), h: Math.abs(e.clientY - dragStart.value.y) }
  if (!tableWrap.value) return
  tableWrap.value.querySelectorAll('.user-table tbody tr.draggable').forEach((row) => {
    const r = row.getBoundingClientRect(); const rect = dragRect.value
    const hit = !(r.right < rect.x || r.left > rect.x + rect.w || r.bottom < rect.y || r.top > rect.y + rect.h)
    const s = new Set(selectedIds.value)
    if (hit) s.add(row.dataset.id); else s.delete(row.dataset.id)
    selectedIds.value = s
  })
}
function onDragUp() { isDragging.value = false; dragRect.value = null }
function clearSel() { selectedIds.value = new Set() }

const toggleSelect = (id) => { if (users.value.find(u => u.id === id && u.role === 'admin')) return; const s = new Set(selectedIds.value); s.has(id) ? s.delete(id) : s.add(id); selectedIds.value = s }
const isAllSelected = computed(() => displayedDeletable.value.length > 0 && displayedDeletable.value.every(d => selectedIds.value.has(d.id)))
const toggleSelectAll = () => {
  if (isAllSelected.value) selectedIds.value = new Set()
  else { const s = new Set(selectedIds.value); displayedDeletable.value.forEach(d => s.add(d.id)); selectedIds.value = s }
}

// ---- 新增 / 编辑 ----
function openAdd() { editing.value = null; form.value = { role: 'patient', account: '', password: '', name: '', dept: '心内科', title: '主治医师', gender: '男', age: 30, bloodType: 'O', phone: '', medicalNo: '' }; showModal.value = true }
function openEdit(u) { editing.value = u; form.value = { role: u.role, account: u.account, password: '', name: u.name, dept: u.dept || '心内科', title: u.title || '主治医师', gender: u.gender || '男', age: u.age || 30, bloodType: u.bloodType || 'O', phone: u.phone || '', medicalNo: u.medicalNo || '' }; showModal.value = true }
function close() { showModal.value = false }

function submit() {
  if (!form.value.account.trim() || !form.value.name.trim()) { showToast('请填写账号与姓名', 'warning'); return }
  if (!editing.value && !form.value.password.trim()) { showToast('请设置初始密码', 'warning'); return }
  try {
    if (editing.value) {
      const patch = { name: form.value.name, phone: form.value.phone }
      if (form.value.password.trim()) patch.password = form.value.password.trim()
      if (form.value.role === 'doctor') { patch.dept = form.value.dept; patch.title = form.value.title }
      else if (form.value.role === 'patient') { patch.gender = form.value.gender; patch.age = Number(form.value.age); patch.bloodType = form.value.bloodType; patch.medicalNo = form.value.medicalNo }
      updateUser(editing.value.id, patch); showToast('用户信息已更新')
    } else { createUser({ ...form.value, age: Number(form.value.age), password: form.value.password.trim() }); showToast('新用户创建成功') }
    close(); load()
  } catch (e) { showToast(e.message, 'warning') }
}

// ---- 删除 ----
function askDelete(u) { confirmDel.value = u }
function doDelete() {
  try { deleteUser(confirmDel.value.id); showToast(`已删除用户「${confirmDel.value.name}」`); confirmDel.value = null; load() }
  catch (e) { showToast(e.message, 'warning'); confirmDel.value = null }
}
function executeBatchDelete() {
  const ids = [...selectedIds.value]; if (!ids.length) { confirmBatchDel.value = false; return }
  let ok = 0
  ids.forEach(id => { try { deleteUser(id); ok++ } catch (e) {} })
  selectedIds.value = new Set(); confirmBatchDel.value = false; load()
  showToast(`已批量删除 ${ok} 个用户`)
}
</script>

<template>
  <div class="user-page">
    <div class="head-desc">管理员权限：对医生 / 患者账户进行新增、修改、删除、查询；可按住左键拖动框选多行删除。</div>

    <section class="toolbar">
      <div class="filters">
        <select v-model="roleFilter" @change="load">
          <option value="all">全部角色</option>
          <option value="doctor">医生</option>
          <option value="patient">患者</option>
        </select>
        <input v-model="search" placeholder="搜索姓名 / 账号" class="search-input" />
      </div>
      <div class="actions">
        <button class="add-btn" @click="openAdd">新增用户</button>
        <button class="batch-btn" @click="confirmBatchDel = true" :disabled="batchCount === 0">删除选中<span v-if="batchCount" class="cnt">{{ batchCount }}</span></button>
        <button v-if="batchCount" class="reset-btn" @click="clearSel">取消</button>
      </div>
    </section>

    <section class="table-card" ref="tableWrap" @mousedown="startDrag">
      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="errorMsg" class="empty error">{{ errorMsg }}</div>
      <template v-else>
        <div class="drag-hint">提示：按住左键拖动框选多行，管理员账户不会出现在可选范围内</div>
        <table v-if="displayed.length" class="user-table">
          <thead><tr>
            <th class="col-check"><input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" /></th>
            <th>账号</th><th>姓名</th><th>角色</th><th>科室/性别</th><th>职称/年龄</th><th>电话</th><th>操作</th>
          </tr></thead>
          <tbody>
            <tr v-for="u in displayed" :key="u.id" :data-id="u.id" class="draggable" :class="[selectedIds.has(u.id) ? 'sel' : '', u.role === 'admin' ? 'no-del' : '']">
              <td class="col-check"><input type="checkbox" :disabled="u.role === 'admin'" :checked="selectedIds.has(u.id)" @change="toggleSelect(u.id)" /></td>
              <td class="mono">{{ u.account }}</td>
              <td class="name">{{ u.name }}</td>
              <td><span class="role-badge" :class="'role-' + u.role">{{ ROLE_LABELS[u.role] }}</span></td>
              <td>{{ u.role === 'doctor' ? u.dept : (u.gender || '-') }}</td>
              <td>{{ u.role === 'doctor' ? u.title : (u.age ? u.age + '岁' : '-') }}</td>
              <td>{{ u.phone || '-' }}</td>
              <td><div class="ops"><button class="op edit" @click="openEdit(u)">修改</button><button v-if="u.role !== 'admin'" class="op del" @click="askDelete(u)">删除</button></div></td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">无匹配用户</div>
        <div v-if="dragRect" class="drag-box" :style="{ left: dragRect.x + 'px', top: dragRect.y + 'px', width: dragRect.w + 'px', height: dragRect.h + 'px' }"></div>
      </template>
    </section>

    <!-- 新增/编辑 -->
    <div v-if="showModal" class="modal-overlay" @click.self="close">
      <div class="modal">
        <div class="modal-head"><h3>{{ editing ? '修改用户' : '新增用户' }}</h3><button class="modal-x" @click="close">✕</button></div>
        <div class="modal-body">
          <div class="row2">
            <label class="f">角色<select v-model="form.role" :disabled="!!editing"><option value="patient">患者</option><option value="doctor">医生</option></select></label>
            <label class="f">账号 *<input v-model="form.account" :disabled="!!editing" /></label>
          </div>
          <div class="row2">
            <label class="f">姓名 *<input v-model="form.name" /></label>
            <label class="f">密码 {{ editing ? '(留空不改)' : '*' }}<input v-model="form.password" type="password" /></label>
          </div>
          <template v-if="form.role === 'doctor'">
            <div class="row2"><label class="f">科室<input v-model="form.dept" /></label><label class="f">职称<input v-model="form.title" /></label></div>
          </template>
          <template v-else>
            <div class="row2">
              <label class="f">性别<select v-model="form.gender"><option value="男">男</option><option value="女">女</option></select></label>
              <label class="f">年龄<input v-model.number="form.age" type="number" min="0" max="150" /></label>
            </div>
            <div class="row2">
              <label class="f">血型<select v-model="form.bloodType"><option value="A">A</option><option value="B">B</option><option value="O">O</option><option value="AB">AB</option></select></label>
              <label class="f">门诊号<input v-model="form.medicalNo" /></label>
            </div>
          </template>
          <label class="f">电话<input v-model="form.phone" /></label>
        </div>
        <div class="modal-foot"><button class="btn cancel" @click="close">取消</button><button class="btn save" @click="submit">{{ editing ? '保存修改' : '确认新增' }}</button></div>
      </div>
    </div>

    <!-- 单删确认 -->
    <div v-if="confirmDel" class="del-overlay" @click.self="confirmDel = null">
      <div class="del-dialog"><div class="del-icon">!</div><h3 class="del-title">确认删除</h3>
        <p class="del-text">确定要删除用户 <b class="del-name">{{ confirmDel.name }}</b><br />（账号：{{ confirmDel.account }}）<br /><span class="del-warn">此操作不可恢复！</span></p>
        <div class="del-btns"><button class="del-cancel" @click="confirmDel = null">取消</button><button class="del-confirm" @click="doDelete">确认删除</button></div>
      </div>
    </div>

    <!-- 批量删除确认 -->
    <div v-if="confirmBatchDel" class="del-overlay" @click.self="confirmBatchDel = false">
      <div class="del-dialog"><div class="del-icon">!</div><h3 class="del-title">批量删除</h3>
        <p class="del-text">确定要批量删除选中的 <b class="del-name">{{ batchCount }}</b> 个用户吗？<br /><span class="del-warn">此操作不可恢复！</span></p>
        <div class="del-btns"><button class="del-cancel" @click="confirmBatchDel = false">取消</button><button class="del-confirm" @click="executeBatchDelete">确认删除</button></div>
      </div>
    </div>

    <div v-if="toast" class="toast" :class="'toast-' + toast.type">{{ toast.msg }}</div>
  </div>
</template>

<style scoped>
.user-page { display: flex; flex-direction: column; gap: 16px; }
.head-desc { padding: 10px 14px; background: #eef6ee; color: #3d6b40; border: 1px solid #d0e4d0; font-size: 0.85rem; }
.toolbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; background: #fff; padding: 12px 16px; border: 1px solid #eef2ee; }
.filters { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.filters select { padding: 8px 10px; border: 1px solid #e0e7e0; font-family: inherit; background: #fff; }
.search-input { padding: 8px 10px; width: 220px; border: 1px solid #e0e7e0; font-family: inherit; }
.actions { display: flex; gap: 8px; align-items: center; }
.add-btn { padding: 9px 18px; border: none; color: #fff; font-weight: 700; cursor: pointer; background: #4a854d; font-family: inherit; }
.add-btn:hover { background: #3d6b40; }
.batch-btn { padding: 9px 14px; border: 1px solid #eee2c8; background: #fff; color: #8a6d3b; font-weight: 700; cursor: pointer; font-family: inherit; }
.batch-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.reset-btn { padding: 9px 14px; border: 1px solid #e0e7e0; background: #fff; color: #6b7280; font-weight: 700; cursor: pointer; font-family: inherit; }
.cnt { display: inline-flex; align-items: center; justify-content: center; min-width: 18px; height: 18px; padding: 0 5px; font-size: 0.68rem; font-weight: 800; background: #d03434; color: #fff; border-radius: 10px; margin-left: 5px; }
.table-card { background: #fff; border: 1px solid #eef2ee; overflow-x: auto; position: relative; }
.drag-hint { padding: 8px 12px; font-size: 0.75rem; color: #93a293; border-bottom: 1px solid #f0f3f0; background: #fbfdfb; }
.user-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; min-width: 720px; }
.user-table th { padding: 10px 12px; text-align: left; background: #f6faf6; color: #557457; border-bottom: 2px solid #dbe8db; }
.user-table td { padding: 10px 12px; border-bottom: 1px solid #f3f4f6; color: #4b5563; }
.user-table tbody tr.draggable { cursor: default; }
.user-table tbody tr.sel { background: #eef6ee; }
.user-table tbody tr.no-del { opacity: 0.6; }
.col-check { width: 40px; text-align: center; }
.mono { font-family: monospace; }
.name { font-weight: 600; color: #1f2937; }
.role-badge { padding: 2px 10px; font-size: 0.76rem; font-weight: 600; }
.role-doctor { background: #e7f1ff; color: #2563eb; }
.role-patient { background: #e6f7ef; color: #2d7d4f; }
.role-admin { background: #fdf0e0; color: #c0392b; }
.ops { display: flex; gap: 6px; }
.op { padding: 4px 12px; border: 1px solid transparent; font-size: 0.78rem; cursor: pointer; font-family: inherit; }
.op.edit { background: #eef2ff; color: #5b6abf; }
.op.del { background: #fde8e8; color: #c0392b; }
.drag-box { position: fixed; background: rgba(74, 133, 77, 0.18); border: 1px solid rgba(74, 133, 77, 0.6); pointer-events: none; z-index: 5; }
.empty { text-align: center; padding: 40px; color: #b0b0b0; }
.empty.error { color: #c0392b; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal { background: #fff; width: 100%; max-width: 520px; max-height: 85vh; overflow-y: auto; }
.modal-head { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; border-bottom: 1px solid #eef2ee; }
.modal-head h3 { margin: 0; font-size: 1.05rem; }
.modal-x { border: none; background: #f3f4f6; width: 28px; height: 28px; cursor: pointer; }
.modal-body { padding: 16px 18px; display: flex; flex-direction: column; gap: 12px; }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.f { display: flex; flex-direction: column; gap: 5px; font-size: 0.82rem; font-weight: 600; color: #4b5563; }
.f input, .f select { padding: 8px 10px; border: 1px solid #e0e7e0; font-family: inherit; font-size: 0.85rem; }
.modal-foot { display: flex; justify-content: flex-end; gap: 10px; padding: 12px 18px; border-top: 1px solid #eef2ee; }
.btn { padding: 8px 18px; border: none; font-weight: 600; cursor: pointer; font-family: inherit; }
.btn.cancel { background: #f3f4f6; color: #6b7280; }
.btn.save { background: #4a854d; color: #fff; }
.toast { position: fixed; top: 20px; right: 20px; z-index: 2000; padding: 10px 16px; color: #fff; font-weight: 600; }
.toast-success { background: #2f9e5f; }
.toast-warning { background: #df8c1a; }
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
