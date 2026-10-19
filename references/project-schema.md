# project.json数据约定

使用UTF-8 JSON，校验脚本仅用Python标准库。按具体项目增补字段，不放认证信息。

必需字段：
- project_id、version：非空项目名和版本，建议v1/v2。
- mode：review / direct / prompts_only。
- stage：planned / plan_approved / images_generated / assets_approved / prompts_ready。
- source：来源名称、version及实际输入依据。
- approvals：数组，每项含scope（plan/images/assets/prompts）、version、evidence（用户确认原话/时间）。可以增加asset_ids/segment_ids限制范围，不能把局部批准升级为全项目。
- assets：数组，含id、type（character/clothing/scene/prop/product/continuity_frame/style）、status（existing/missing/candidate/approved/generated/failed）、name。所有图像生成项加prompt与生成结果路径；衣服关联角色用owner。
- segments：数组，每项含id、title、scene_id、global_start、duration、references与shots。
- references：每项index从1递增，asset_id真实存在，role说明职责；首帧另设first_frame_asset_id，不默认为图1。
- shots：每项id、start、end、characters（人物asset_id）、action、camera、end_state。可加dialogue（speaker人物asset_id、text、offscreen布尔值）、props_before/props_after和cut_reason。

所有时间用秒数，片段局部从0开始。多个片段默认在全片上连续；有意留空段在项目声明allow_global_gaps=true。镜号在全项目唯一，通常S02-A-01；完整视频提示词可在该片段显示镜头1，表格同时保留唯一ID。

验证命令：
```bash
python scripts/validate_project.py /absolute/path/project.json
```

返回0表示结构检查通过，1表示错误，2表示无法解析输入。它不校验医学内容、画面质量、人格一致性或真实的生成许可；审核证据必须由当前会话核对。输出WARN是待人工判断的对白时长或高密度动作，并非禁止执行。
