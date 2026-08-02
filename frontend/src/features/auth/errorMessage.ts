import { ApiError } from '../../shared/api/client.ts'

export function authErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === 'VALIDATION_ERROR') {
      return 'Проверьте заполнение полей и повторите попытку.'
    }
    if (error.code === 'NOT_AUTHENTICATED') {
      return 'Имя пользователя или пароль не подошли.'
    }

    return error.message
  }

  return 'Не удалось связаться с сервером. Проверьте соединение и попробуйте ещё раз.'
}
