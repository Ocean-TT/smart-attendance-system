const API_BASE_URL = 'http://localhost:8000/api'

const getAuthHeader = () => {
  const token = localStorage.getItem('token')
  if (!token) return {}
  try {
    // 对 Token 进行 Base64 编码，以支持中文用户名在 Header 中的传输
    const safeToken = btoa(encodeURIComponent(token))
    return { 'Authorization': `Bearer ${safeToken}` }
  } catch (e) {
    return { 'Authorization': `Bearer ${token}` }
  }
}

export const loginApi = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })

  return response.json()
}

export const registerApi = async (userData) => {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  })

  return response.json()
}

export const faceLoginApi = async (faceData) => {
  const response = await fetch(`${API_BASE_URL}/auth/face-login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ faceData }),
  })

  return response.json()
}

export const getDashboardOverview = async () => {
  const response = await fetch(`${API_BASE_URL}/dashboard/overview`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
  })

  return response.json()
}

// ===== 课堂会话相关 =====
export const startClass = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/start`, {
    method: 'POST',
    headers: getAuthHeader()
  })
  return response.json()
}

export const stopClass = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/stop`, {
    method: 'POST',
    headers: getAuthHeader()
  })
  return response.json()
}

export const joinClassroom = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/join`, {
    method: 'POST',
    headers: getAuthHeader()
  })
  return response.json()
}

export const leaveClassroom = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/leave`, {
    method: 'POST',
    headers: getAuthHeader()
  })
  return response.json()
}

export const getJoinedStudents = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/joined_students`, {
    headers: getAuthHeader()
  })
  return response.json()
}

// ===== 教室相关 =====
export const startAttendance = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/attendance/start`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    }
  })
  if (!response.ok) throw new Error('签到启动失败')
  return response.json()
}

export const getAttendanceStatus = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/attendance/status`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取签到状态失败')
  return response.json()
}

export const stopAttendance = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/attendance/stop`, {
    method: 'POST',
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('停止签到失败')
  return response.json()
}

export const studentCheckin = async (classId, faceData) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/attendance/checkin`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ faceData })
  })
  if (!response.ok) throw new Error('签到失败')
  return response.json()
}

export const randomCall = async (classId, strategy) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/call/random`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ strategy })
  })
  if (!response.ok) throw new Error('随机点名失败')
  return response.json()
}

export const resetCall = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/call/reset`, {
    method: 'POST',
    headers: getAuthHeader()
  })
  return response.json()
}

export const rateStudent = async (studentId, score) => {
  const response = await fetch(`${API_BASE_URL}/classroom/call/rate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ student_id: studentId, score })
  })
  if (!response.ok) throw new Error('评分失败')
  return response.json()
}

export const startClassroomQuestion = async (classId, data) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/question/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify(data)
  })
  return response.json()
}

export const getClassroomQuestionStatus = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/question/status`, {
    headers: getAuthHeader()
  })
  return response.json()
}

export const submitClassroomAnswer = async (classId, answer) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/question/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ answer })
  })
  return response.json()
}

export const stopClassroomQuestion = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/question/stop`, {
    method: 'POST',
    headers: getAuthHeader()
  })
  return response.json()
}

export const stopSession = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/attendance/stop`, {
    method: 'POST',
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('结束会话失败')
  return response.json()
}

export const getClassrooms = async () => {
  const response = await fetch(`${API_BASE_URL}/classroom/list`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取班级列表失败')
  return response.json()
}

export const getClassroomDetails = async (id) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${id}`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取班级详情失败')
  return response.json()
}

export const updateClassroom = async (id, data) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${id}`, {
    method: 'PUT',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('更新班级信息失败')
  return response.json()
}

export const getAnnouncements = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/announcements`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取公告失败')
  return response.json()
}

export const createAnnouncement = async (classId, content) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/announcements`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ content })
  })
  if (!response.ok) throw new Error('发布公告失败')
  return response.json()
}

export const deleteAnnouncement = async (annId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/announcements/${annId}`, {
    method: 'DELETE',
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('删除公告失败')
  return response.json()
}

export const getClassroomStudents = async (id) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${id}/students`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取学生列表失败')
  return response.json()
}

export const addStudentToClass = async (classId, studentId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/add-student`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ student_id: studentId })
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '添加学生失败')
  }
  return response.json()
}

export const removeStudentFromClass = async (classId, studentId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}/students/${studentId}`, {
    method: 'DELETE',
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('移除学生失败')
  return response.json()
}

export const createClassroom = async (classData) => {
  const response = await fetch(`${API_BASE_URL}/classroom/create`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify(classData)
  })
  if (!response.ok) throw new Error('创建班级失败')
  return response.json()
}

export const deleteClassroom = async (classId) => {
  const response = await fetch(`${API_BASE_URL}/classroom/${classId}`, {
    method: 'DELETE',
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('删除班级失败')
  return response.json()
}

// ===== 题库相关 =====
export const getQuestionBanks = async () => {
  const response = await fetch(`${API_BASE_URL}/questions/banks`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取题库列表失败')
  return response.json()
}

export const getQuestionsInBank = async (bankId) => {
  const response = await fetch(`${API_BASE_URL}/questions/banks/${bankId}/questions`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取题目列表失败')
  return response.json()
}

export const createQuestion = async (bankId, question) => {
  const response = await fetch(`${API_BASE_URL}/questions/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ bank_id: bankId, ...question })
  })
  if (!response.ok) throw new Error('创建题目失败')
  return response.json()
}

export const updateQuestion = async (questionId, question) => {
  const response = await fetch(`${API_BASE_URL}/questions/${questionId}`, {
    method: 'PUT',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify(question)
  })
  if (!response.ok) throw new Error('更新题目失败')
  return response.json()
}

export const submitPractice = async (data) => {
  const response = await fetch(`${API_BASE_URL}/questions/practice/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('提交练习结果失败')
  return response.json()
}

export const deleteQuestion = async (questionId) => {
  const response = await fetch(`${API_BASE_URL}/questions/${questionId}`, {
    method: 'DELETE',
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('删除题目失败')
  return response.json()
}

// ===== 统计相关 =====
export const getStudentStats = async (studentId) => {
  const response = await fetch(`${API_BASE_URL}/stats/student/${studentId}`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取学生统计失败')
  return response.json()
}

export const getTeacherOverview = async (classId = null) => {
  let url = `${API_BASE_URL}/stats/teacher/overview`
  if (classId) {
    url += `?class_id=${classId}`
  }
  const response = await fetch(url, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取教师概览失败')
  return response.json()
}

// ===== 用户相关 =====
export const getProfile = async () => {
  const response = await fetch(`${API_BASE_URL}/user/profile`, {
    headers: getAuthHeader()
  })
  if (!response.ok) throw new Error('获取用户资料失败')
  return response.json()
}

export const updateProfile = async (profileData) => {
  const response = await fetch(`${API_BASE_URL}/user/profile`, {
    method: 'PUT',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify(profileData)
  })
  if (!response.ok) throw new Error('更新用户资料失败')
  return response.json()
}

export const updateFace = async (faceData) => {
  const response = await fetch(`${API_BASE_URL}/user/face/update`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ face_data: faceData })
  })
  if (!response.ok) throw new Error('更新人脸数据失败')
  return response.json()
}

export const changePassword = async (oldPwd, newPwd) => {
  const response = await fetch(`${API_BASE_URL}/user/password/change`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      ...getAuthHeader()
    },
    body: JSON.stringify({ old_pwd: oldPwd, new_pwd: newPwd })
  })
  if (!response.ok) throw new Error('修改密码失败')
  return response.json()
}
