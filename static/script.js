/**
 * AuthService Frontend Logic (Stateless with HttpOnly Cookies)
 */

const logOutput = document.getElementById("log-output");

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

/**
 * Выводит данные в блок терминала на странице
 * @param {string} title - Заголовок действия
 * @param {any} data - Данные для отображения (объект или строка)
 */
function log(title, data) {
  const time = new Date().toLocaleTimeString();
  let displayData = data;

  if (typeof data === "object") {
    displayData = JSON.stringify(data, null, 2);
  }

  const message = `[${time}] --- ${title} ---\n${displayData}\n\n`;
  // Добавляем новый лог в начало
  logOutput.textContent = message + logOutput.textContent;
}

/**
 * Очистка окна логов
 */
function clearLogs() {
  logOutput.textContent = "Logs cleared. Ready for new commands...";
}

// --- УПРАВЛЕНИЕ МОДАЛЬНЫМ ОКНОМ ---

function openModal() {
  document.getElementById("registerModal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("registerModal").classList.add("hidden");
}

// Закрытие модалки при клике вне её области
window.onclick = function (event) {
  const modal = document.getElementById("registerModal");
  if (event.target === modal) {
    closeModal();
  }
};

// --- API ЗАПРОСЫ ---

/**
 * РЕГИСТРАЦИЯ (POST /register)
 * Отправляет JSON с данными нового пользователя
 */
async function submitRegistration() {
  const name = document.getElementById("reg-name").value;
  const lastName = document.getElementById("reg-last-name").value;
  const fatherName = document.getElementById("reg-father-name").value;
  const email = document.getElementById("reg-email").value;
  const password = document.getElementById("reg-password").value;
  const confirm = document.getElementById("reg-confirm").value;

  if (!name || !lastName || !email || !password) {
    alert("Пожалуйста, заполните все обязательные поля (*)");
    return;
  }

  if (password !== confirm) {
    alert("Пароли не совпадают!");
    return;
  }

  const payload = {
    email: email,
    password: password,
    password_repeat: confirm,
    name: name,
    last_name: lastName,
    father_name: fatherName || null,
  };

  try {
    const response = await fetch("/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    log("API: REGISTER", { status: response.status, data });

    if (response.ok) {
      alert("Регистрация успешна! Теперь вы можете войти.");
      closeModal();
      document.getElementById("login-email").value = email;
    }
  } catch (err) {
    log("ERROR: REGISTER", err.message);
  }
}

/**
 * ВХОД (POST /login)
 * Получает куки от сервера. В теле ответа токенов больше нет (они в Set-Cookie)
 */
async function login() {
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  try {
    const response = await fetch("/api/v1/auth/login", {
      method: "POST",
      body: formData, // OAuth2 ожидает x-www-form-urlencoded
    });

    const data = await response.json();
    log("API: LOGIN", {
      status: response.status,
      message: data.message || "Check cookies in Application tab",
    });
  } catch (err) {
    log("ERROR: LOGIN", err.message);
  }
}

/**
 * ПОЛУЧЕНИЕ ПРОФИЛЯ (GET /me)
 * Браузер автоматически прикрепляет access_token из куки
 */
async function getMe() {
  try {
    const response = await fetch("/api/v1/users/me");
    const data = await response.json();

    log("API: GET /ME", { status: response.status, data });

    if (response.status === 401) {
      log("SYSTEM", "Access token expired or missing. Try 'Refresh Session'.");
    }
  } catch (err) {
    log("ERROR: GET_ME", err.message);
  }
}

/**
 * ОБНОВЛЕНИЕ СЕССИИ (POST /refresh)
 * Использует refresh_token из куки для получения нового access_token
 */
async function refreshToken() {
  try {
    const response = await fetch("/api/v1/auth/refresh", {
      method: "POST",
    });

    const data = await response.json();
    log("API: REFRESH", { status: response.status, data });
  } catch (err) {
    log("ERROR: REFRESH", err.message);
  }
}

/**
 * ВЫХОД (POST /logout)
 * Сервер пришлет инструкции на удаление кук
 */
async function logout() {
  try {
    const response = await fetch("/api/v1/users/logout", {
      method: "POST",
    });

    const data = await response.json();
    log("API: LOGOUT", data);

    // Очищаем интерфейс после выхода
    if (response.ok) {
      log("SYSTEM", "Stateless Logout Complete. Cookies cleared by server.");
    }
  } catch (err) {
    log("ERROR: LOGOUT", err.message);
  }
}
