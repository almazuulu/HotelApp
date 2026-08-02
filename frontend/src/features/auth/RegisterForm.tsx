import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import { Link, useNavigate } from 'react-router-dom'

import { useApiClient } from '../../shared/api/useApiClient.ts'
import type { RegistrationPayload } from '../../shared/api/types.ts'
import { accountQueryKey } from './accountQuery.ts'
import { authErrorMessage } from './errorMessage.ts'

export function RegisterForm() {
  const api = useApiClient()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { register, handleSubmit, formState: { errors } } = useForm<RegistrationPayload>()
  const registrationMutation = useMutation({
    mutationFn: (payload: RegistrationPayload) => api.auth.register(payload),
    onSuccess: (user) => {
      queryClient.setQueryData(accountQueryKey, user)
      navigate('/account', { replace: true })
    },
  })

  return (
    <Form noValidate onSubmit={handleSubmit((values) => registrationMutation.mutate(values))}>
      <div className="form-grid">
        <Form.Group className="mb-3" controlId="register-first-name">
          <Form.Label>Имя</Form.Label>
          <Form.Control
            autoComplete="given-name"
            isInvalid={errors.first_name !== undefined}
            {...register('first_name', { required: 'Введите имя.' })}
          />
          <Form.Control.Feedback type="invalid">{errors.first_name?.message}</Form.Control.Feedback>
        </Form.Group>
        <Form.Group className="mb-3" controlId="register-last-name">
          <Form.Label>Фамилия</Form.Label>
          <Form.Control
            autoComplete="family-name"
            isInvalid={errors.last_name !== undefined}
            {...register('last_name', { required: 'Введите фамилию.' })}
          />
          <Form.Control.Feedback type="invalid">{errors.last_name?.message}</Form.Control.Feedback>
        </Form.Group>
      </div>
      <Form.Group className="mb-3" controlId="register-username">
        <Form.Label>Имя пользователя</Form.Label>
        <Form.Control
          autoComplete="username"
          isInvalid={errors.username !== undefined}
          {...register('username', { required: 'Придумайте имя пользователя.' })}
        />
        <Form.Control.Feedback type="invalid">{errors.username?.message}</Form.Control.Feedback>
      </Form.Group>
      <Form.Group className="mb-3" controlId="register-email">
        <Form.Label>Email</Form.Label>
        <Form.Control
          type="email"
          autoComplete="email"
          isInvalid={errors.email !== undefined}
          {...register('email', { required: 'Укажите email.' })}
        />
        <Form.Control.Feedback type="invalid">{errors.email?.message}</Form.Control.Feedback>
      </Form.Group>
      <Form.Group className="mb-3" controlId="register-phone">
        <Form.Label>Телефон</Form.Label>
        <Form.Control
          type="tel"
          autoComplete="tel"
          isInvalid={errors.phone !== undefined}
          {...register('phone', { required: 'Укажите телефон.' })}
        />
        <Form.Control.Feedback type="invalid">{errors.phone?.message}</Form.Control.Feedback>
      </Form.Group>
      <Form.Group className="mb-4" controlId="register-password">
        <Form.Label>Пароль</Form.Label>
        <Form.Control
          type="password"
          autoComplete="new-password"
          isInvalid={errors.password !== undefined}
          {...register('password', { required: 'Придумайте пароль.', minLength: { value: 8, message: 'Минимум 8 символов.' } })}
        />
        <Form.Control.Feedback type="invalid">{errors.password?.message}</Form.Control.Feedback>
      </Form.Group>
      {registrationMutation.isError ? (
        <p className="form-alert" role="alert">{authErrorMessage(registrationMutation.error)}</p>
      ) : null}
      <Button className="hotel-primary-button w-100" disabled={registrationMutation.isPending} type="submit">
        {registrationMutation.isPending ? 'Создаём аккаунт…' : 'Создать аккаунт'}
      </Button>
      <p className="auth-switch">
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </Form>
  )
}
