## WebSocket Commands

### `bridge/entity/remove`

Remove a entity from the entity registry

#### Schema

- `type: <string>` **(Required)** - Must be: `bridge/entity/remove`
- `service_slug: <string>` **(Required)** - The slug for the service that the entity belongs to. *Example:* `climate_manager`
- `device_slug: <string>` **(Required)** - The slug for the device that the entity belongs to. *Example:* `living_room_climate`
- `entity_slug: <string>` **(Required)** - The slug for the entity. *Example:* `temperature`

### `bridge/entity/available`

Marks the availability of an entity.

#### Schema

- `type: <string>` **(Required)** - Must be: `bridge/entity/add`
- `service_slug: <string>` **(Required)** - The slug for the service that the entity belongs to. *Example:* `climate_manager`
- `device_slug: <string>` **(Required)** - The slug for the device that the entity belongs to. *Example:* `living_room_climate`
- `entity_slug: <string>` **(Required)** - The slug for the entity. *Example:* `temperature`
- `available: <bool>` **(Required)** - If the entity is available.

### `bridge/entity/add`

Add (discover) new entities and devices

#### Schema

- `type: <string>` **(Required)** - Must be: `bridge/entity/add`
- `service_slug: <string>` **(Required)** - The slug for the service that the entity belongs to. *Example:* `climate_manager`
- `device_slug: <string>` **(Required)** - The slug for the device that the entity belongs to. *Example:* `living_room_climate`
- `entity_slug: <string>` **(Required)** - The slug for the entity. *Example:* `temperature`
- `device_info: <dict>` **(Required)** - Device information. *Example:* `{ "name": "Device1" }`
- `platform: <string>` **(Required)** - The platform of the entity. *Example:* `sensor`
- `state: <bool, str, int, float, None>` (Optional) - The new state of the entity. *Example:* `25.6`\
- `attributes: <dict>` (Optional) - Updated attributes of the entity. *Example:* `{ "attr1": "Hello world!" }`

### `bridge/entity/state`

Update entity state and/or attributes

#### Schema

- `type: <string>` **(Required)** - Must be: `bridge/entity/state`
- `service_slug: <string>` **(Required)** - The slug for the service that the entity belongs to. *Example:* `climate_manager`
- `device_slug: <string>` **(Required)** - The slug for the device that the entity belongs to. *Example:* `living_room_climate`
- `entity_slug: <string>` **(Required)** - The slug for the entity. *Example:* `temperature`
- `state: <bool, str, int, float, None>` (Optional) - The new state of the entity. *Example:* `25.6`
- `attributes: <dict>` (Optional) - Updated attributes of the entity. *Example:* `{ "attr1": "Hello world!" }`

### `bridge/entity/config`

Update the config of an entity

#### Schema

- `type: <string>` **(Required)** - Must be: `bridge/entity/update`
- `service_slug: <string>` **(Required)** - The slug for the service that the entity belongs to. *Example:* `climate_manager`
- `device_slug: <string>` **(Required)** - The slug for the device that the entity belongs to. *Example:* `living_room_climate`
- `entity_slug: <string>` **(Required)** - The slug for the entity. *Example:* `temperature`
- `config: <dict>` **(Required)**
    - `name: <string>` (Optional) - The name to give to the entity.*Example:* `Living room temperature`
    - `icon: <string>` (Optional) - The icon to give to the entity. *Example:* `mdi:thermometer`
    - Additional platform specific config is allowed.

### `bridge/entity/event`

Trigger an event entity

#### Schema

- `type` **(Required)** - Must be: `bridge/entity/event`
- `service_slug` **(Required)** - The slug for the service that the event entity belongs to. *Example:* `scene_manager`
- `device_slug` **(Required)** - The slug for the device that the event entity belongs to. *Example:* `living_room_scenes`
- `entity_slug` **(Required)** - The slug for the event entity. *Example:* `scene_fired`
- `event_type` **(Required)** - The event type to fire. *Example:* `scene_fired`
- `event_data` (Optional) - Optional data to send with the event. *Example:* `{ "message": "Hello world!" }`