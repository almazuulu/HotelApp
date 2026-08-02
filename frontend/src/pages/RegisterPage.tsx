import { AuthFrame } from '../features/auth/AuthFrame.tsx'
import { RegisterForm } from '../features/auth/RegisterForm.tsx'

export function RegisterPage() {
  return (
    <AuthFrame eyebrow="Новый гость" title="Создайте аккаунт">
      <p className="auth-card-lead">Он понадобится для бронирований и управления контактными данными.</p>
      <RegisterForm />
    </AuthFrame>
  )
}
