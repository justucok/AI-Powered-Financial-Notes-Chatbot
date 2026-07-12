import axios from 'axios'

const AUTH_TOKEN_KEY = 'auth_token'
const AUTH_FULL_NAME_KEY = 'auth_full_name'
const AUTH_NICKNAME_KEY = 'auth_nickname'
const AUTH_GREETING_KEY = 'auth_greeting'

// ---------------------------------------------------------------------------
// Token storage helpers
// ---------------------------------------------------------------------------

/**
 * Save the JWT token, full name, and nickname to localStorage.
 * @param {string} token
 * @param {string} fullName
 * @param {string} nickname
 */
export function saveAuthData(token, fullName, nickname, greeting) {
  localStorage.setItem(AUTH_TOKEN_KEY, token)
  localStorage.setItem(AUTH_FULL_NAME_KEY, fullName)
  localStorage.setItem(AUTH_NICKNAME_KEY, nickname)
  if (greeting) {
    localStorage.setItem(AUTH_GREETING_KEY, greeting)
  }
}

/**
 * Return the stored JWT token, or null if not present.
 * @returns {string|null}
 */
export function getToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

/**
 * Return the stored full name, or null if not logged in.
 * @returns {string|null}
 */
export function getFullName() {
  return localStorage.getItem(AUTH_FULL_NAME_KEY)
}

/**
 * Return the stored nickname preference.
 * @returns {string|null}
 */
export function getNickname() {
  return localStorage.getItem(AUTH_NICKNAME_KEY)
}

export function getGreeting() {
  return localStorage.getItem(AUTH_GREETING_KEY) || 'Kak'
}

/**
 * Remove the token, full name, and nickname from localStorage (logout).
 */
export function removeAuthData() {
  localStorage.removeItem(AUTH_TOKEN_KEY)
  localStorage.removeItem(AUTH_FULL_NAME_KEY)
  localStorage.removeItem(AUTH_NICKNAME_KEY)
  localStorage.removeItem(AUTH_GREETING_KEY)
}

/**
 * Return true if a JWT token is stored in localStorage.
 * @returns {boolean}
 */
export function isLoggedIn() {
  return Boolean(getToken())
}

// ---------------------------------------------------------------------------
// Auth API calls
// ---------------------------------------------------------------------------

const authClient = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || '/api' })

/**
 * Register a new user account with extended info.
 * @param {object} param0
 * @param {string} param0.email
 * @param {string} param0.full_name
 * @param {string} param0.nickname
 * @param {string} param0.password
 * @returns {Promise<{message: string}>}
 */
export async function register({ email, full_name, nickname, gender, password }) {
  const response = await authClient.post('/v1/auth/register', {
    email,
    full_name,
    nickname,
    gender,
    password,
  })
  return response.data
}

/**
 * Login using email and password.
 * Automatically saves auth details to localStorage.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{access_token: string, token_type: string, full_name: string, nickname: string}>}
 */
export async function login(email, password) {
  const response = await authClient.post('/v1/auth/login', { email, password })
  saveAuthData(
    response.data.access_token, 
    response.data.full_name, 
    response.data.nickname,
    response.data.preferred_greeting
  )
  return response.data
}

export async function forgotPassword(email) {
  const response = await authClient.post('/v1/auth/forgot-password', { email })
  return response.data
}

export async function resetPassword(token, new_password) {
  const response = await authClient.post('/v1/auth/reset-password', { token, new_password })
  return response.data
}

/**
 * Log out the current user.
 */
export function logout() {
  removeAuthData()
}
