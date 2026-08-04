import { useQuery } from '@tanstack/react-query'

import { useApiClient } from '../../shared/api/useApiClient.ts'
import type { Amenity, RoomType, RoomTypeFilters } from '../../shared/api/types.ts'

/** Drops an empty amenity list so an unfiltered call and a `{amenity: []}` call share one cache entry. */
function normalizeFilters(filters: RoomTypeFilters): RoomTypeFilters {
  const amenity = filters.amenity !== undefined && filters.amenity.length > 0 ? [...filters.amenity].sort() : undefined

  return { adults: filters.adults, children: filters.children, amenity }
}

export function roomTypesQueryKey(filters: RoomTypeFilters) {
  return ['catalog', 'room-types', normalizeFilters(filters)] as const
}

export function useRoomTypes(filters: RoomTypeFilters = {}) {
  const api = useApiClient()
  const normalized = normalizeFilters(filters)

  return useQuery({
    queryKey: roomTypesQueryKey(normalized),
    queryFn: () => api.catalog.listRoomTypes(normalized),
    staleTime: 60 * 1000,
  })
}

export function roomTypeQueryKey(slug: string) {
  return ['catalog', 'room-type', slug] as const
}

export function useRoomType(slug: string) {
  const api = useApiClient()

  return useQuery({
    queryKey: roomTypeQueryKey(slug),
    queryFn: () => api.catalog.getRoomType(slug),
    staleTime: 60 * 1000,
  })
}

/** Derives the public amenity vocabulary from a set of categories; there is no dedicated amenities endpoint. */
export function collectAmenities(roomTypes: RoomType[]): Amenity[] {
  const bySlug = new Map<string, Amenity>()
  for (const roomType of roomTypes) {
    for (const amenity of roomType.amenities) {
      bySlug.set(amenity.slug, amenity)
    }
  }

  return [...bySlug.values()].sort((a, b) => a.name.localeCompare(b.name, 'ru'))
}
