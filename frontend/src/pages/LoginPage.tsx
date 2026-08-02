import { AuthFrame } from '../features/auth/AuthFrame.tsx'
import { LoginForm } from '../features/auth/LoginForm.tsx'

export function LoginPage() {
  return (
    <AuthFrame eyebrow="Гостевой доступ" title="С возвращением">
      <p className="auth-card-lead">Войдите, чтобы продолжить работу с личным кабинетом.</p>
      <LoginForm />
    </AuthFrame>
  )
}
