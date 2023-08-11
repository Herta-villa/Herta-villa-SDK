# 贡献指南

首先，感谢你愿意抽出时间为 Herta SDK 贡献自己的力量。

对于不同的行为（包括但不限于提出 Issue、发起 Pull Request 修复 Bug 或增加新功能、仓库管理及工作流程），我们提供了一个目录，可按需查阅相关部分。

此外，在社区内进行讨论请保持和善、互相包容，避免发生冲突争执。

建议阅读：

- [提问的智慧](https://github.com/ryanhanwu/How-To-Ask-Questions-The-Smart-Way/blob/main/README-zh_CN.md)
- [贡献者公约](./CODE_OF_CONDUCT.md)

## 目录

- [提出 Issue](#提出-issue)
  - [提出 Bug](#提出-bug)
  - [提出建议以及 API 等的变动](#提出建议)
- [开发环境](#开发环境)
- [代码及提交要求](#代码及提交要求)
- [代码结构](#代码结构)
- [增加、改动或删除 API](#增加改动或删除-api)
- [增加、改动或删除事件](#增加改动或删除事件)
- [增加、改动或删除消息段](#增加改动或删除消息段)
- [发起 Pull Request](#发起-pull-requestpr)
- [仓库工作流](#仓库工作流)

## 提出 Issue

请注意，开发者并没有义务回复你的问题。你应该具备基本的提问技巧。

### 提出 Bug

请在提出 Issue 时提供相关的运行环境（如 Python 版本、SDK 版本、系统信息等），准确的问题描述（使用的功能、预期与实际发生），以及相关日志等。

按照「Bug 反馈」问题模板填写相关信息。

### 提出建议

请明确说明提出你的目的，以及可行的实现方式。

按照「提出建议」问题模板填写信息。

有一种例外：API、事件、返回模型等发生变动时，请使用「提出 API 变动」模板并填写相关信息。

## 开发环境

可使用 `pdm install` 安装环境；

使用 `pre-commit install` 安装 pre-commit hook。

可以使用 `test.py` 作为测试用的入口，此文件已被忽略。

## 代码及提交要求

- 代码遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)（代码样式）和 [PEP 408](https://www.python.org/dev/peps/pep-0408/)（类型标注）规范
- 代码需经过 ruff linter（可使用 `pdm run lint` 执行）的检查
  - 自动修复可以使用 `pdm run fix`
  - 建议使用 pre-commit hook
- docstrings 使用 [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Commit Message 使用 [gitmoji](https://gitmoji.dev)

## 代码结构

Herta SDK 代码结构比较简单。

- [apis (Package)](./hertavilla/apis/) 负责实现 API 的请求。
- [message (Package)](./hertavilla/message/) 负责实现各种消息段。
- [server (Package)](./hertavilla/server/) 负责实现后端。
- [bot (Module)](./hertavilla/bot.py) 负责实现 VillaBot 以及 Handler 的注册执行。
- [event (Module)](./hertavilla/event.py) 负责实现事件模型。
- [match (Module)](./hertavilla/match.py) 负责实现消息匹配。
- [model (Module)](./hertavilla/model.py) 负责实现 API 返回等模型。
- 其他。

各包下的 `internal` 模块一般为定义基类的模块。

## 增加、改动或删除 API

API 使用 Mixin，在各 Mixin 类编写 API 实现，然后 Mixin 到 `VillaBot` 类。

首先，前往此 API 所在类别指定的模块。

如果不存在请创建新模块，编写 Mixin 类（命名为 `{类型}Mixin`），继承 `hertavilla.apis.internal` 的 `_BaseAPIMixin`



> 类别遵循 [大别野文档](https://webstatic.mihoyo.com/vila/bot/doc/) 的 URL。
>
> 例如：大别野 api 的文档 URL 为：`https://webstatic.mihoyo.com/vila/bot/doc/villa_api/`
>
> 则取 `villa` 作为类别。

然后，增加、改动或删除 API。（需要编写 API 文档）

> self.base_request 提供了请求接口，按 Type Hints 填写参数；
>
> URL Param 使用 `params` 传递，GET 请求的参数使用此方法传递；
>
> JSON Data 使用 `data` 传递，POST 请求的参数使用此方法传递；
>
> **请勿在使用 GET 方法时传递 JSON Data**。
>
> 需要权限的 API 需要传入 `villa_id`，需要权限的 API 可参考 [接口权限表](https://webstatic.mihoyo.com/vila/bot/doc/permissions.html)

> 简单模型（如返回值只为一个 key 的可以直接返回，如[图片转存 API](https://github.com/Herta-villa/Herta-villa-SDK/blob/master/hertavilla/apis/img.py#L21-L28)）
>
> 复杂模型需前往模块 `model` 定义

最后，如果你新建了类别，请前往模块 `bot` 导入你新建的 Mixin 类。

## 增加、改动或删除事件

Event 的命名遵循 `{事件名称}Event` 的格式，如 [JoinVilla](https://webstatic.mihoyo.com/vila/bot/doc/callback.html###JoinVilla) 事件命名为 `JoinVillaEvent`。

继承 `Event` 基类，type 的类型标注为 `Literal[{type值}]`，SDK 会自动注册事件。

模型根据文档提供填写即可。

## 增加、改动或删除消息段

仿照包 `message` 中的模块进行更改。

如果新增了消息段，需要到 `hertavilla.message.chain` 修改 `MessageChain` 的 `to_content_json` 方法。

<!-- *（其他更改待施工）* -->

## 发起 Pull Request（PR）

- 所有的 PR 的目标为 `dev` 分支，切忌目标选为 `master`；

- PR 的描述明确更改内容；

- 请根据 PR 的内容按需选择标签，以确保 CHANGELOG 正确生成。

  - 如果改动体现出破坏性（Breaking），标签需同时选择 `💥breaking`，并明确说明旧代码更新的方法。

## 仓库工作流

- 建议所有的更改都通过 PR 合并到 `dev` 分支
- 发版时，发起由 `dev` 分支到 `master` 分支的 PR，标题为版本号，如 `0.8.0`；标签选择 `release`。CI 会自动更新代码中的版本并发布。
