import type { components } from './generated/schema.d.ts'

export type ApiErrorCode = components['schemas']['ApiErrorCode']
export type ApiErrorPayload = components['schemas']['ApiError']
export type AccountUser = components['schemas']['User']
export type LoginPayload = components['schemas']['Login']
export type RegistrationPayload = components['schemas']['Registration']
export type ProfileUpdatePayload = components['schemas']['PatchedUser']
export type HeroSlide = components['schemas']['HeroSlide']
export type HotelFeature = components['schemas']['HotelFeature']
export type SiteContent = components['schemas']['SiteContent']
export type Amenity = components['schemas']['Amenity']
export type RoomTypeImage = components['schemas']['RoomTypeImage']
export type ConfirmationMode = components['schemas']['ConfirmationModeEnum']
export type RoomType = components['schemas']['RoomType']
export type BookingStatus = components['schemas']['StatusEnum']
export type Booking = components['schemas']['Booking']
export type BookingList = components['schemas']['BookingList']
export type QuoteRequest = components['schemas']['QuoteRequest']
export type Quote = components['schemas']['Quote']

/** Public catalog query filters; mirrors `inventory.RoomTypeFilterSerializer` on the backend. */
export interface RoomTypeFilters {
  adults?: number
  children?: number
  amenity?: string[]
}
