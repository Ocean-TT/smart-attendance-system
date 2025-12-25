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
### 一. 登录/注册模块

#### 1. 用户注册

- **描述**: 创建一个新的用户账户（教师或学生）。

- **请求路径**: `POST /api/auth/register`

- **请求头**: `Content-Type: application/json`

- 请求参数:

  ```
  {
    "username": "user202401",
    "password": "a_strong_password",
    "role": "STUDENT", // 或 "TEACHER"
    "studentId": "20240001", // 学生必填
    "name": "张三"
  }
  ```

- 返回响应 (成功):

  ```
  {
    "code": 201,
    "msg": "用户创建成功",
    "data": {
      "userId": "uuid-for-zhangsan",
      "username": "user202401"
    }
  }
  ```

#### 2. 用户登录

- **描述**: 用户使用凭证登录系统，获取访问令牌(Token)。

- **请求路径**: `POST /api/auth/login`

- **请求头**: `Content-Type: application/json`

- 请求参数:

  ```
  {
    "username": "user202401",
    "password": "a_strong_password"
  }
  ```

- 返回响应 (成功):

  ```
  {
    "code": 200,
    "msg": "登录成功",
    "data": {
      "token": "a.very.long.jwt.token.string",
      "expiresIn": 7200
    }
  }
  ```

#### 3. 获取当前用户信息

- **描述**: 获取当前已登录用户的详细信息。

- **请求路径**: `GET /api/auth/me`

- **请求头**: `Authorization: Bearer {token}`

- **请求参数**: (无)

- 返回响应 (成功):

  ```
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "userId": "uuid-for-zhangsan",
      "username": "user202401",
      "role": "STUDENT",
      "name": "张三",
      "studentId": "20240001"
    }
  }
  ```

#### 4. 用户登出

- **描述**: 用户登出系统，使其访问令牌失效。

- **请求路径**: `POST /api/auth/logout`

- **请求头**: `Authorization: Bearer {token}`

- **请求参数**: (无)

- 返回响应 (成功):

  ```
  {
    "code": 200,
    "msg": "登出成功",
    "data": null
  }
  ```

### 二. 班级与学生管理模块

#### 1. 创建班级

- **描述**: 教师创建一个新的班级。

- **请求路径**: `POST /api/classes`

- **请求头**: `Authorization: Bearer {token}`

- 请求参数:

- ```
  {
    "name": "计算机网络 2025春季班",
    "description": "本课程讲解TCP/IP协议栈..."
  }
  ```

- 返回响应 (成功):

  ```
  {
    "code": 201,
    "msg": "班级创建成功",
    "data": {
      "classId": "uuid-for-class",
      "name": "计算机网络 2025春季班",
      "teacherId": "uuid-for-teacher"
    }
  }
  ```

#### 2. 获取班级列表

- **描述**: 获取当前用户（教师或学生）关联的所有班级列表。

- **请求路径**: `GET /api/classes`

- **请求头**: `Authorization: Bearer {token}`

- **请求参数**: (无)

- 返回响应 (成功):

  ```
  {
    "code": 200,
    "msg": "获取成功",
    "data": [
      {
        "classId": "uuid-for-class-1",
        "name": "计算机网络 2025春季班"
      },
      {
        "classId": "uuid-for-class-2",
        "name": "操作系统原理"
      }
    ]
  }
  ```

#### 3. 获取班级详情（含学生名单）

- **描述**: 获取单个班级的详细信息，包括完整的学生花名册。

- **请求路径**: `GET /api/classes/{classId}`

- **请求头**: `Authorization: Bearer {token}`

- **请求参数**: (无，`classId`在路径中)

- 返回响应 (成功):

  ```
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "classId": "uuid-for-class-1",
      "name": "计算机网络 2025春季班",
      "students": [
        { "userId": "uuid-for-student-1", "name": "张三", "studentId": "20240001" },
        { "userId": "uuid-for-student-2", "name": "李四", "studentId": "20240002" }
      ]
    }
  }
  ```

#### 4. 向班级中添加学生

- 

- **描述**: 教师向指定班级批量添加学生。

- **请求路径**: `POST /api/classes/{classId}/students`

- **请求头**: `Authorization: Bearer {token}`

- 请求参数:

- ```
  {
    "studentIds": ["20240003", "20240004"]
  }
  ```

- 返回响应 (成功):

```
{
  "code": 200,
  "msg": "操作完成",
  "data": {
    "addedCount": 2,
    "failedCount": 0,
    "failures": []
  }
}
```

#### 5. 从班级中移除学生

- **描述**: 教师从指定班级中移除一个学生。

- **请求路径**: `DELETE /api/classes/{classId}/students/{studentUserId}`

- **请求头**: `Authorization: Bearer {token}`

- **请求参数**: (无，`classId`和`studentUserId`在路径中)

- 返回响应 (成功):

  ```
  {
    "code": 200,
    "msg": "学生已从班级移除",
    "data": null
  }
  ```

### 三.题库管理模块

#### 1. 创建题目

- **描述**: 教师为指定课程创建一个新题目。
- **请求路径**: `POST /api/questions`
- **请求头**: `Authorization: Bearer {token}`
- 请求参数:
  ```json
  {
    "courseId": "uuid-for-course",
    "type": "SINGLE_CHOICE",
    "content": "在TCP/IP协议中，哪一层负责处理网络间的路由选择？",
    "options": [
      { "key": "A", "value": "应用层" },
      { "key": "B", "value": "传输层" },
      { "key": "C", "value": "网络层" },
      { "key": "D", "value": "数据链路层" }
    ],
    "answer": ["C"],
    "tags": ["网络协议", "期中"]
  }
  ```
- 返回响应 (成功):
  ```json
  {
    "code": 201,
    "msg": "题目创建成功",
    "data": {
      "questionId": "uuid-for-new-question"
    }
  }
  ```

#### 2. 获取题目列表

- **描述**: 获取指定课程下的题目列表，支持分页和筛选。
- **请求路径**: `GET /api/questions`
- **请求头**: `Authorization: Bearer {token}`
- 请求参数 (Query):
  - `courseId` (string, 必填): 课程ID。
  - `type` (string, 可选): 题目类型。
  - `tag` (string, 可选): 标签。
  - `page` (number, 可选, 默认1): 页码。
  - `pageSize` (number, 可选, 默认10): 每页数量。
- 返回响应 (成功):
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "total": 150,
      "page": 1,
      "pageSize": 10,
      "items": [
        {
          "questionId": "uuid-for-question-1",
          "type": "SINGLE_CHOICE",
          "content": "在TCP/IP协议中..."
        }
      ]
    }
  }
  ```

#### 3. 获取单个题目详情

- **描述**: 获取一个题目的完整详细信息。
- **请求路径**: `GET /api/questions/{questionId}`
- **请求头**: `Authorization: Bearer {token}`
- 请求参数: (无)
- 返回响应 (成功):
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "questionId": "uuid-for-question-1",
      "courseId": "uuid-for-course",
      "type": "SINGLE_CHOICE",
      "content": "在TCP/IP协议中，哪一层负责处理网络间的路由选择？",
      "options": [
        { "key": "A", "value": "应用层" },
        { "key": "B", "value": "传输层" },
        { "key": "C", "value": "网络层" },
        { "key": "D", "value": "数据链路层" }
      ],
      "answer": ["C"],
      "tags": ["网络协议", "期中"]
    }
  }
  ```

#### 4. 更新题目

- **描述**: 修改一个已存在的题目。
- **请求路径**: `PUT /api/questions/{questionId}`
- **请求头**: `Authorization: Bearer {token}`
- 请求参数: (与创建题目类似，包含需要修改的字段)
- 返回响应 (成功):
  ```json
  {
    "code": 200,
    "msg": "题目更新成功",
    "data": {
      "questionId": "uuid-for-updated-question"
    }
  }
  ```

#### 5. 删除题目

- **描述**: 从题库中删除一个题目。
- **请求路径**: `DELETE /api/questions/{questionId}`
- **请求头**: `Authorization: Bearer {token}`
- 请求参数: (无)
- 返回响应 (成功):
  ```json
  {
    "code": 200,
    "msg": "题目删除成功",
    "data": null
  }
  ```

### 四. 人脸识别考勤模块

#### 1. 录入人脸信息

- **描述**: 学生首次在系统中录入自己的人脸照片，作为后续识别的档案。
- **请求路径**: `POST /api/face/register`
- **请求头**: `Authorization: Bearer {token}`, `Content-Type: multipart/form-data`
- 请求参数:
  - `image` (file): 包含清晰人脸的照片文件。
- 返回响应 (成功):
  ```json
  {
    "code": 201,
    "msg": "人脸信息录入成功",
    "data": {
      "userId": "uuid-for-student",
      "faceRegistered": true
    }
  }
  ```

#### 2. 人脸识别签到

- **描述**: 在教师发起的考勤活动中，学生通过上传实时照片进行人脸识别签到。
- **请求路径**: `POST /api/attendance/checkin/face`
- **请求头**: `Authorization: Bearer {token}`, `Content-Type: multipart/form-data`
- 请求参数:
  - `attendanceId` (string): 当前正在进行的考勤活动ID。
  - `image` (file): 学生通过设备摄像头实时捕捉的人脸照片。
- 返回响应 (成功):
  ```json
  {
    "code": 200,
    "msg": "签到成功",
    "data": {
      "recordId": "uuid-for-attendance-record",
      "checkInTime": "2025-12-25T10:00:00Z",
      "status": "PRESENT"
    }
  }
  ```
- 返回响应 (失败 - 人脸不匹配):
  ```json
  {
    "code": 400,
    "msg": "人脸不匹配，请重试",
    "data": null
  }
  ```


### 五. 智能点名模块

#### 1. 随机点名

- **描述**: 教师从指定班级中，根据策略随机抽取一名学生进行提问。
- **请求路径**: `POST /api/roll-call/random`
- **请求头**: `Authorization: Bearer {token}`
- 请求参数:
  ```json
  {
    "classId": "uuid-for-class",
    "strategy": "RANDOM"
  }
  ```
- 返回响应 (成功):
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "student": {
        "userId": "uuid-for-student",
        "name": "李四",
        "studentId": "20240002"
      },
      "rollCallId": "uuid-for-this-roll-call"
    }
  }
  ```

#### 2. 记录课堂表现

- **描述**: 教师为被点名的学生记录本次课堂互动表现。
- **请求路径**: `POST /api/roll-call/record`
- **请求头**: `Authorization: Bearer {token}`
- 请求参数:
  ```json
  {
    "rollCallId": "uuid-for-this-roll-call",
    "studentUserId": "uuid-for-student",
    "performance": "EXCELLENT"
  }
  ```
- 返回响应 (成功):
  ```json
  {
    "code": 201,
    "msg": "表现记录成功",
    "data": {
      "recordId": "uuid-for-performance-record"
    }
  }
  ```

### 六. 智能问答模块

- #### 1. 发起课堂提问

  - **描述**: 教师选定一个题目后，发起一次课堂提问，系统将随机点名一名学生来回答。

  - **请求路径**: `POST /api/class-questions/start`

  - **请求头**: `Authorization: Bearer {token}`

  - 请求参数:

  - ```
    {
      "classId": "uuid-for-class",
      "questionId": "uuid-for-the-chosen-question"
    }
    ```

  - 返回响应 (成功):

  - ```
    {
      "code": 200,
      "msg": "提问发起成功",
      "data": {
        "questioningSessionId": "uuid-for-this-session",
        "question": {
          "questionId": "uuid-for-the-chosen-question",
          "content": "在TCP/IP协议中，哪一层负责处理网络间的路由选择？"
        },
        "selectedStudent": {
          "userId": "uuid-for-student-li-si",
          "name": "李四",
          "studentId": "20240002"
        }
      }
    }
    ```

  - 返回响应 (失败 - 班级为空):

  - ```
    {
      "code": 400,
      "msg": "无法提问，当前班级没有学生",
      "data": null
    }
    ```

#### 2. 公布答案

- **描述**: 教师在提问互动结束后，请求并向全班公布该题目的参考答案。**注意**: 这个API本质上是调用了题库模块的功能，这里为了文档清晰而单独列出。

- **请求路径**: `GET /api/questions/{questionId}`

- **请求头**: `Authorization: Bearer {token}`

- **请求参数**: (无，`questionId`在路径中)

- 返回响应 (成功):

  ```
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "questionId": "uuid-for-the-chosen-question",
      "content": "在TCP/IP协议中...",
      "answer": ["C"],
      "analysis": "网络层的主要任务是实现网络互连，进而实现数据包的路由和转发..."
    }
  }
  ```

### 七.数据统计与展示模块

#### 1. 获取考勤统计

- **描述**: 获取指定班级的历史考勤统计数据，包括总体出勤率和每位学生的详细情况。
- **请求路径**: `GET /api/statistics/attendance`
- **请求头**: `Authorization: Bearer {token}`
- **请求参数 (Query)**:
  - `classId` (string, 必填): 班级ID。
- **返回响应 (成功)**:
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "classId": "uuid-for-class",
      "totalSessions": 20,
      "averageAttendanceRate": 0.95,
      "studentStats": [
        {
          "userId": "uuid-for-student-1",
          "name": "张三",
          "presentCount": 19,
          "absentCount": 1,
          "lateCount": 2
        }
      ]
    }
  }
  ```

#### 2. 获取点名表现统计

- **描述**: 获取指定班级的点名互动表现统计。
- **请求路径**: `GET /api/statistics/roll-call`
- **请求头**: `Authorization: Bearer {token}`
- **请求参数 (Query)**:
  - `classId` (string, 必填): 班级ID。
- **返回响应 (成功)**:
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "classId": "uuid-for-class",
      "totalRollCalls": 50,
      "performanceDistribution": {
        "EXCELLENT": 15,
        "GOOD": 25,
        "POOR": 10
      },
      "mostCalledStudents": [
         {
          "userId": "uuid-for-student-2",
          "name": "李四",
          "calledCount": 5
        }
      ]
    }
  }
  ```

#### 3. 获取问答活跃度统计

- **描述**: 获取指定班级的问答社区活跃度统计。
- **请求路径**: `GET /api/statistics/qa`
- **请求头**: `Authorization: Bearer {token}`
- **请求参数 (Query)**:
  - `classId` (string, 必填): 班级ID。
- **返回响应 (成功)**:
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "classId": "uuid-for-class",
      "totalQuestions": 30,
      "totalAnswers": 120,
      "mostActiveStudents": [
        {
          "userId": "uuid-for-student-1",
          "name": "张三",
          "questionsAsked": 5,
          "answersProvided": 20
        }
      ]
    }
  }
  ```









