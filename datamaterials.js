
<script setup>
import { ref, computed } from 'vue'
import { materialCategories, materials } from '../data/materials.js'

// 当前选中的分类
const activeCategory = ref('past-papers')

// 当前分类资料
const currentMaterials = computed(() => {
  return materials[activeCategory.value] || []
})

// 当前分类名称
const currentCategoryName = computed(() => {
  return materialCategories.find(
    item => item.key === activeCategory.value
  )?.label || '建模资料'
})
</script>

<template>
  <main class="materials-page">

    <!-- 页面标题 -->
    <header class="page-header">
      <h1 class="section-title">建模资料</h1>
      <p class="page-description">
        汇集数学建模竞赛相关学习资料、历年赛题、
        优秀论文及常用编程工具教程。
      </p>
    </header>

    <!-- 飞书知识库总入口 -->
    <section class="knowledge-section">
      <div class="knowledge-content">
        <div>
          <h2>飞书知识库</h2>
          <p>
            校队数学建模学习资料统一存放入口，
            点击进入查看完整资料目录。
          </p>
        </div>

        <a
          href="#"
          target="_blank"
          rel="noopener noreferrer"
          class="knowledge-link"
        >
          进入知识库
          <span aria-hidden="true">↗</span>
        </a>
      </div>
    </section>

    <!-- 资料分类 -->
    <section class="category-section">
      <h2 class="section-title">资料分类</h2>

      <nav class="category-nav" aria-label="资料分类">
        <button
          v-for="category in materialCategories"
          :key="category.key"
          type="button"
          class="category-button"
          :class="{
            active: activeCategory === category.key
          }"
          :aria-pressed="activeCategory === category.key"
          @click="activeCategory = category.key"
        >
          {{ category.label }}
        </button>
      </nav>
    </section>

    <!-- 资料列表 -->
    <section class="list-section">
      <div class="list-heading">
        <h2 class="section-title">
          {{ currentCategoryName }}
        </h2>

        <span class="material-count">
          共 {{ currentMaterials.length }} 份资料
        </span>
      </div>

      <!-- 有资料时展示列表 -->
      <template v-if="currentMaterials.length > 0">

        <!-- 表头 -->
        <div class="material-row material-table-header">
          <span class="material-name">资料名称</span>
          <span class="material-meta">格式 / 大小</span>
          <span class="material-action">资料链接</span>
        </div>

        <!-- 资料内容 -->
        <div
          v-for="item in currentMaterials"
          :key="item.id"
          class="material-row"
        >
          <div class="material-name">
            <span class="file-icon" aria-hidden="true">
              ↳
            </span>
            <span>{{ item.name }}</span>
          </div>

          <div class="material-meta">
            <span class="file-format">{{ item.format }}</span>
            <span class="file-size">{{ item.size }}</span>
          </div>

          <div class="material-action">
            <a
              :href="item.feishuUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="material-link"
            >
              前往飞书查看
              <span aria-hidden="true">↗</span>
            </a>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-else class="placeholder-block">
        <div class="placeholder-symbol" aria-hidden="true">
          +
        </div>

        <p class="placeholder-title">
          整理中，敬请期待
        </p>

        <p class="placeholder-description">
          {{ currentCategoryName }}相关资料正在整理，
          后续将陆续上传至飞书知识库。
        </p>
      </div>
    </section>

    <!-- 页面说明 -->
    <footer class="materials-footer">
      <p>
        所有资料均通过飞书云文档提供，请勿将内部资料
        用于未经授权的传播。
      </p>
    </footer>

  </main>
</template>

<style scoped>
.materials-page {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 32px 64px;
  background: #ffffff;
  color: #333333;
  box-sizing: border-box;
}

/* 页面标题 */

.page-header {
  margin-bottom: 42px;
}

.section-title {
  margin: 0;
  padding-left: 14px;
  border-left: 4px solid #710a53;
  color: #222222;
  font-size: 21px;
  font-weight: 600;
  line-height: 1.4;
}

.page-description {
  margin: 16px 0 0 18px;
  color: #777777;
  font-size: 14px;
  line-height: 1.9;
}

/* 飞书知识库入口 */

.knowledge-section {
  margin-bottom: 48px;
  border-top: 1px solid #e8e8e8;
  border-bottom: 1px solid #e8e8e8;
}

.knowledge-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 28px 18px;
}

.knowledge-content h2 {
  margin: 0 0 10px;
  color: #333333;
  font-size: 18px;
  font-weight: 600;
}

.knowledge-content p {
  margin: 0;
  color: #888888;
  font-size: 14px;
  line-height: 1.8;
}

.knowledge-link {
  flex-shrink: 0;
  color: #710a53;
  font-size: 14px;
  text-decoration: none;
  border-bottom: 1px solid #710a53;
  padding-bottom: 4px;
  transition: color 0.2s;
}

.knowledge-link:hover {
  color: #a52a78;
}

/* 分类导航 */

.category-section {
  margin-bottom: 42px;
}

.category-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  margin-top: 24px;
  border-bottom: 1px solid #e8e8e8;
}

.category-button {
  position: relative;
  padding: 12px 22px;
  border: none;
  background: transparent;
  color: #777777;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
}

.category-button:hover {
  color: #710a53;
}

.category-button.active {
  color: #710a53;
  font-weight: 600;
}

.category-button.active::after {
  position: absolute;
  right: 18px;
  bottom: -1px;
  left: 18px;
  height: 2px;
  background: #710a53;
  content: '';
}

/* 列表标题 */

.list-section {
  min-height: 280px;
}

.list-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}

.material-count {
  color: #999999;
  font-size: 13px;
}

/* 资料列表 */

.material-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px 150px;
  align-items: center;
  gap: 20px;
  min-height: 62px;
  padding: 12px 16px;
  border-bottom: 1px solid #eeeeee;
  box-sizing: border-box;
}

.material-table-header {
  min-height: 42px;
  background: #fafafa;
  color: #888888;
  font-size: 13px;
}

.material-name {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  color: #444444;
  font-size: 14px;
  line-height: 1.7;
}

.file-icon {
  flex-shrink: 0;
  color: #710a53;
  font-size: 16px;
}

.material-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #888888;
  font-size: 13px;
}

.file-format {
  color: #666666;
}

.file-size {
  color: #999999;
}

.material-action {
  text-align: right;
}

.material-link {
  color: #710a53;
  font-size: 13px;
  text-decoration: none;
  white-space: nowrap;
}

.material-link:hover {
  text-decoration: underline;
}

/* 空状态 */

.placeholder-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 260px;
  border-top: 1px solid #eeeeee;
  border-bottom: 1px solid #eeeeee;
  text-align: center;
}

.placeholder-symbol {
  margin-bottom: 14px;
  color: #aaaaaa;
  font-size: 30px;
  font-weight: 300;
}

.placeholder-title {
  margin: 0 0 10px;
  color: #555555;
  font-size: 15px;
  font-weight: 500;
}

.placeholder-description {
  margin: 0;
  color: #999999;
  font-size: 13px;
  line-height: 1.8;
}

/* 页面底部 */

.materials-footer {
  margin-top: 54px;
  padding-top: 20px;
  border-top: 1px solid #eeeeee;
}

.materials-footer p {
  margin: 0;
  color: #aaaaaa;
  font-size: 12px;
  line-height: 1.8;
}

/* 移动端适配 */

@media (max-width: 768px) {
  .materials-page {
    padding: 28px 18px 48px;
  }

  .page-header {
    margin-bottom: 32px;
  }

  .knowledge-content {
    align-items: flex-start;
    flex-direction: column;
    padding: 22px 12px;
    gap: 18px;
  }

  .category-nav {
    gap: 4px;
  }

  .category-button {
    padding: 12px 14px;
    font-size: 13px;
  }

  .material-row {
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 6px 12px;
    padding: 14px 10px;
  }

  .material-table-header {
    display: none;
  }

  .material-name {
    grid-column: 1 / -1;
    font-size: 14px;
  }

  .material-meta {
    grid-column: 1;
    font-size: 12px;
  }

  .material-action {
    grid-column: 2;
    grid-row: 2;
    text-align: right;
  }

  .material-count {
    font-size: 12px;
  }
}

@media (max-width: 380px) {
  .materials-page {
    padding-right: 14px;
    padding-left: 14px;
  }

  .category-button {
    padding-right: 10px;
    padding-left: 10px;
  }

  .material-row {
    padding-right: 4px;
    padding-left: 4px;
  }
}
</style>
