# 🌳 分支管理策略

## 📋 分支结构

本项目采用双分支管理模式，确保开发和生产环境的分离：

### 🚀 main 分支（开发环境）
- **用途**: 开发环境的默认主分支
- **特点**: 
  - 包含最新的开发功能
  - 允许直接推送和合并
  - 用于日常开发和功能测试
  - 集成最新的功能特性和Bug修复

### 🏭 prod 分支（生产管理）
- **用途**: 生产环境管理分支
- **特点**:
  - 包含稳定的生产版本代码
  - 严格的代码审查流程
  - 只接受来自 main 分支的合并请求
  - 用于正式版本发布

## 🔄 工作流程

### 开发流程
1. **日常开发**: 在 `main` 分支进行功能开发
2. **功能测试**: 在 `main` 分支进行测试和调试
3. **代码审查**: 确保代码质量和功能完整性
4. **生产发布**: 将稳定的 `main` 分支合并到 `prod` 分支

### 版本发布流程
```bash
# 1. 切换到 main 分支进行开发
git checkout main

# 2. 开发完成后推送到 main
git push origin main

# 3. 测试通过后切换到 prod 分支
git checkout prod

# 4. 合并 main 分支到 prod
git merge main

# 5. 推送生产版本
git push origin prod

# 6. 创建版本标签
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0
```

## 📦 分支保护规则

### main 分支
- ✅ 允许直接推送
- ✅ 允许强制推送（开发阶段）
- ✅ 允许删除（管理员）

### prod 分支
- ❌ 禁止直接推送
- ❌ 禁止强制推送
- ❌ 禁止删除
- ✅ 只允许通过 Pull Request 合并

## 🏷️ 版本标签策略

### 版本号规则
采用语义化版本控制 (Semantic Versioning)：
- **主版本号**: 重大功能变更或不兼容的API修改
- **次版本号**: 新增功能，向下兼容
- **修订版本号**: Bug修复，向下兼容

### 标签示例
- `v2.1.0` - 添加统计功能的重要版本
- `v2.1.1` - 修复统计功能Bug
- `v2.2.0` - 添加高级OBS集成功能

## 📝 提交信息规范

### 提交类型
- `✨ feat`: 新功能
- `🐛 fix`: Bug修复
- `📚 docs`: 文档更新
- `🎨 style`: 代码格式调整
- `♻️ refactor`: 代码重构
- `⚡ perf`: 性能优化
- `✅ test`: 测试相关
- `🔧 chore`: 构建过程或辅助工具的变动

### 提交信息格式
```
<类型>(<范围>): <描述>

[可选的正文]

[可选的脚注]
```

### 示例
```
✨ feat(statistics): 添加场景切换统计功能

- 新增 switch_statistics.py 统计管理器
- 集成 SQLite 数据库存储切换记录
- 支持实时统计和整点报告

Closes #1
```

## 🛠️ 分支管理命令

### 常用命令
```bash
# 查看所有分支
git branch -a

# 切换分支
git checkout main
git checkout prod

# 创建并切换到新分支
git checkout -b feature/new-feature

# 合并分支
git merge main

# 删除本地分支
git branch -d feature/old-feature

# 删除远程分支
git push origin --delete feature/old-feature
```

### 同步分支
```bash
# 从远程获取最新代码
git fetch origin

# 合并远程分支到本地
git merge origin/main
git merge origin/prod
```

## 🚨 注意事项

1. **永远不要直接在 prod 分支开发**
2. **确保 main 分支的代码经过充分测试**
3. **生产发布前必须进行完整的功能验证**
4. **使用有意义的提交信息**
5. **定期同步远程分支**

---

📅 **创建时间**: 2025-08-31  
📝 **最后更新**: 2025-08-31  
👤 **维护者**: OBS智能监控系统开发团队