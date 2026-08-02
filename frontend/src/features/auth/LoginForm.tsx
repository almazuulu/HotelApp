import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import { Link, useNavigate } from 'react-router-dom'

import { useApiClient } from '../../shared/api/useApiClient.ts'
import type { LoginPayload } from '../../shared/api/types.ts'
import { accountQueryKey } from './accountQuery.ts'
import { authErrorMessage } from './errorMessage.ts'

export function LoginForm() {
  const api = useApiClient()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { register, handleSubmit, formState: { errors } } = useForm<LoginPayload>()
  const loginMutation = useMutation({
    mutationFn: (payload: LoginPayload) => api.auth.login(payload),
    onSuccess: (user) => {
      queryClient.setQueryData(accountQueryKey, user)
      navigate('/account', { replace: true })
    },
  })

  return (
    <Form noValidate onSubmit={handleSubmit((values) => loginMutation.mutate(values))}>
      <Form.Group className="mb-3" controlId="login-username">
        <Form.Label>Имя пользователя</Form.Label>
        <Form.Control
          autoComplete="username"
          isInvalid={errors.username !== undefined}
          {...register('username', { required: 'Введите имя пользователя.' })}
        />
        <Form.Control.Feedback type="invalid">{errors.username?.message}</Form.Control.Feedback>
      </Form.Group>
      <Form.Group className="mb-4" controlId="login-password">
        <Form.Label>Пароль</Form.Label>
        <Form.Control
          type="password"
          autoComplete="current-password"
          isInvalid={errors.password !== undefined}
          {...register('password', { required: 'Введите пароль.' })}
        />
        <Form.Control.Feedback type="invalid">{errors.password?.message}</Form.Control.Feedback>
      </Form.Group>
      {loginMutation.isError ? (
        <p className="form-alert" role="alert">{authErrorMessage(loginMutation.error)}</p>
      ) : null}
      <Button className="hotel-primary-button w-100" disabled={loginMutation.isPending} type="submit">
        {loginMutation.isPending ? 'Входим…' : 'Войти в аккаунт'}
      </Button>
      <p className="auth-switch">
        Впервые здесь? <Link to="/register">Создать аккаунт</Link>
      </p>
    </Form>
  )
}
