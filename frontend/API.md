# 课堂考勤与点名提问系统 API 文档

## 统一响应格式

所有接口均返回以下 JSON 格式：

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

- **code**: 状态码（200 成功, 400 参数错误, 401 未认证, 403 禁止, 404 不存在, 500 服务器错误）
- **msg**: 消息描述
- **data**: 返回数据（失败时可为 null）

---

## API 接口模板

### eg： 获取课程问答统计
- **描述**: 获取某课程的问答活跃度统计
- **请求路径**: `GET /api/statistics/qa`
- **请求头**: `Authorization: Bearer {token}`
- **请求参数**:
  | 参数名 | 位置 | 类型 | 必填 | 说明 |
  | :--- | :--- | :--- | :--- | :--- |
  | courseId | Query | String | 是 | 课程ID |
- **返回响应**:
  ```json
  {
    "code": 200,
    "msg": "success",
    "data": {
      "courseName": "string",
      "totalQuestions": "number",
      "answeredCount": "number",
      "unansweredCount": "number",
      "mostActiveStudents": [
        {
          "studentId": "string",
          "name": "string",
          "questionsAsked": "number",
          "answersProvided": "number"
        }
      ]
    }
  }
  ```

### [模块名称]

#### [序号] [接口名称]

- **描述**: 
- **请求路径**: 
- **请求方法**: 
- **请求头**: 
- **请求参数**:
  ```json
  {
  }
  ```
- **返回响应**:
  ```json
  {
    "code": 200,
    "msg": "success",
    "data": {}
  }
  ```

---

## 各模块 API 列表

### 1. 课程管理模块
- [ ] 待补充

### 2. 课堂考勤管理模块
- [ ] 待补充

### 3. 智能点名提问模块
- [ ] 待补充

### 4. 智能问答模块
- [ ] 待补充

### 5. 数据统计和展示模块
- [ ] 待补充

### 6. 用户管理模块
- [ ] 待补充

---

## 版本历史

| 版本 | 修改内容 | 修改日期   | 修改人 |
| :--- | :------- | :--------- | :----- |
| v1.0 | 初版模板 | 2025-12-24 | 团队   |