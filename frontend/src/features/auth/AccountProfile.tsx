import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import Button from 'react-bootstrap/Button'
import Form from 'react-bootstrap/Form'
import { Navigate, useNavigate } from 'react-router-dom'

import { ApiError } from '../../shared/api/client.ts'
import { useApiClient } from '../../shared/api/useApiClient.ts'
import type { AccountUser } from '../../shared/api/types.ts'
import { accountQueryKey, useCurrentUser } from './accountQuery.ts'
import { AuthFrame } from './AuthFrame.tsx'
import { authErrorMessage } from './errorMessage.ts'

type ProfileFormValues = Pick<AccountUser, 'username' | 'email' | 'first_name' | 'last_name' | 'phone'>

const emptyProfile: ProfileFormValues = {
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
}

export function AccountProfile() {
  const api = useApiClient()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const currentUser = useCurrentUser()
  const { register, handleSubmit, reset, formState: { errors } } = useForm<ProfileFormValues>({
    defaultValues: emptyProfile,
  })
  const updateMutation = useMutation({
    mutationFn: (payload: ProfileFormValues) => api.auth.updateProfile(payload),
    onSuccess: (user) => {
      queryClient.setQueryData(accountQueryKey, user)
      reset(user)
    },
  })
  const logoutMutation = useMutation({
    mutationFn: () => api.auth.logout(),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: accountQueryKey })
      navigate('/login', { replace: true })
    },
  })

  useEffect(() => {
    if (currentUser.data !== undefined) {
      reset(currentUser.data)
    }
  }, [currentUser.data, reset])

  if (currentUser.isPending) {
    return <p className="page-status">Загружаем профиль…</p>
  }
  if (currentUser.error instanceof ApiError && currentUser.error.code === 'NOT_AUTHENTICATED') {
    return <Navigate replace to="/login" />
  }
  if (currentUser.error !== null || currentUser.data === undefined) {
    return <p className="page-status" role="alert">{authErrorMessage(currentUser.error)}</p>
  }

  return (
    <AuthFrame
      actions={
        <button
          className="hotel-logout-button"
          disabled={logoutMutation.isPending}
          onClick={() => logoutMutation.mutate()}
          type="button"
        >
          {logoutMutation.isPending ? 'Выходим…' : 'Выйти'}
        </button>
      }
      eyebrow="Личный кабинет"
      title={`Здравствуйте, ${currentUser.data.first_name}`}
    >
      <p className="auth-card-lead">Здесь можно обновить контактные данные для будущих бронирований.</p>
      <Form noValidate onSubmit={handleSubmit((values) => updateMutation.mutate(values))}>
        <div className="form-grid">
          <Form.Group className="mb-3" controlId="account-first-name">
            <Form.Label>Имя</Form.Label>
            <Form.Control
              autoComplete="given-name"
              isInvalid={errors.first_name !== undefined}
              {...register('first_name', { required: 'Введите имя.' })}
            />
            <Form.Control.Feedback type="invalid">{errors.first_name?.message}</Form.Control.Feedback>
          </Form.Group>
          <Form.Group className="mb-3" controlId="account-last-name">
            <Form.Label>Фамилия</Form.Label>
            <Form.Control
              autoComplete="family-name"
              isInvalid={errors.last_name !== undefined}
              {...register('last_name', { required: 'Введите фамилию.' })}
            />
            <Form.Control.Feedback type="invalid">{errors.last_name?.message}</Form.Control.Feedback>
          </Form.Group>
        </div>
        <Form.Group className="mb-3" controlId="account-username">
          <Form.Label>Имя пользователя</Form.Label>
          <Form.Control
            autoComplete="username"
            isInvalid={errors.username !== undefined}
            {...register('username', { required: 'Введите имя пользователя.' })}
          />
          <Form.Control.Feedback type="invalid">{errors.username?.message}</Form.Control.Feedback>
        </Form.Group>
        <Form.Group className="mb-3" controlId="account-email">
          <Form.Label>Email</Form.Label>
          <Form.Control
            type="email"
            autoComplete="email"
            isInvalid={errors.email !== undefined}
            {...register('email', { required: 'Укажите email.' })}
          />
          <Form.Control.Feedback type="invalid">{errors.email?.message}</Form.Control.Feedback>
        </Form.Group>
        <Form.Group className="mb-4" controlId="account-phone">
          <Form.Label>Телефон</Form.Label>
          <Form.Control
            type="tel"
            autoComplete="tel"
            isInvalid={errors.phone !== undefined}
            {...register('phone', { required: 'Укажите телефон.' })}
          />
          <Form.Control.Feedback type="invalid">{errors.phone?.message}</Form.Control.Feedback>
        </Form.Group>
        {updateMutation.isError ? (
          <p className="form-alert" role="alert">{authErrorMessage(updateMutation.error)}</p>
        ) : null}
        {updateMutation.isSuccess ? <p className="form-success">Данные сохранены.</p> : null}
        <Button className="hotel-primary-button w-100" disabled={updateMutation.isPending} type="submit">
          {updateMutation.isPending ? 'Сохраняем…' : 'Сохранить изменения'}
        </Button>
      </Form>
    </AuthFrame>
  )
}
