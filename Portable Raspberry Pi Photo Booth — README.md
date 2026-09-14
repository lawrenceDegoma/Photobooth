# Portable Raspberry Pi Photo Booth

A self-contained, portable photo booth built around a **Raspberry Pi 3 Model B+**, Raspberry Pi Camera Module, touchscreen display, and integrated lighting.

The booth should operate as a standalone appliance. A user should be able to power it on, take a series of photos through a touchscreen interface, generate a traditional photo strip, and download their photos to their phone through a QR code.

The system should **not require an external computer, internet connection, or external network during normal operation**.

---

# 1. Project Goals

The primary goal is to create a polished portable photo booth that is:

- Self-contained
- Portable
- Battery-capable
- Touchscreen controlled
- Easy for nontechnical users
- Functional without internet
- Reliable enough for multi-hour events
- Modular and maintainable
- Optimized for the Raspberry Pi 3's limited resources
- Extensible for future features

The application should feel like a dedicated photo booth rather than a Raspberry Pi running a Python program.

After initial configuration, normal users should never need to interact with Raspberry Pi OS.

---

# 2. Target User Experience

The normal flow should be:

```text
POWER ON
    ↓
Automatic Boot
    ↓
Photo Booth Application Launches
    ↓
Welcome Screen
    ↓
"Tap to Start"
    ↓
Live Camera Preview
    ↓
Start Session
    ↓
3 → 2 → 1
    ↓
Capture Photo
    ↓
Repeat for 4 Photos
    ↓
Generate Photo Strip
    ↓
Final Preview
    ↓
Retake / Keep
    ↓
QR Code
    ↓
Download Photos
    ↓
Finish
    ↓
Return to Welcome Screen
```

No keyboard or mouse should be required.

---

# 3. Target Hardware

Initial target hardware:

```text
Raspberry Pi 3 Model B+
│
├── Raspberry Pi Camera Module 3
├── 7" Raspberry Pi Touch Display
├── Integrated LED lighting
├── Physical capture button (optional)
├── USB/removable photo storage (optional)
├── 20,000–30,000 mAh battery
└── Portable enclosure + tripod mount
```

The application should remain reasonably hardware-independent where possible.

Hardware-specific behavior should be isolated behind interfaces so components can eventually be replaced without rewriting the main application.

---

# 4. Raspberry Pi 3 Constraints

The Raspberry Pi 3 Model B+ has significantly fewer resources than modern desktop hardware.

Design accordingly.

Important constraints:

- 1 GB RAM
- Limited ARM CPU performance
- Limited thermal headroom
- SD-card storage
- Limited I/O bandwidth
- Battery-powered operation
- Potential thermal throttling

Avoid unnecessary:

- background processes
- Electron applications
- browser-based kiosk interfaces
- containers in production
- large ML models
- real-time AI processing
- excessive OpenCV processing
- unnecessary databases
- high-frequency disk writes

Prefer lightweight native Python components.

---

# 5. Proposed Software Stack

Primary language:

```text
Python 3
```

Recommended components:

```text
UI
└── PyQt6

Camera
└── Picamera2

Image Processing
├── Pillow
└── OpenCV only where necessary

QR Generation
└── qrcode

Local Sharing Server
└── Flask

Hardware
└── gpiozero

Configuration
└── YAML

Logging
└── Python logging

Application Startup
└── systemd
```

Dependencies should be kept minimal.

Do not introduce additional frameworks unless there is a clear architectural justification.

---

# 6. High-Level Architecture

```text
                  ┌─────────────────────┐
                  │      Photo Booth    │
                  │     Application     │
                  └──────────┬──────────┘
                             │
          ┌──────────────────┼───────────────────┐
          │                  │                   │
          ▼                  ▼                   ▼
   ┌─────────────┐    ┌─────────────┐     ┌─────────────┐
   │ UI Manager  │    │   Session   │     │   Config    │
   │             │    │   Manager   │     │   Manager   │
   └──────┬──────┘    └──────┬──────┘     └─────────────┘
          │                  │
          │          ┌───────┼────────┐
          │          │       │        │
          ▼          ▼       ▼        ▼
       Camera      Image   Storage   Sharing
       Service    Service  Service   Service
          │                           │
          ▼                           ▼
     Pi Camera                   Local Server
                                      │
                                      ▼
                                  QR Code
```

Each subsystem should have a clearly defined responsibility.

Avoid putting business logic directly inside UI classes.

---

# 7. Repository Structure

Recommended structure:

```text
photobooth/
│
├── README.md
├── requirements.txt
├── pyproject.toml
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── application.py
│   │   ├── config.py
│   │   ├── events.py
│   │   └── state.py
│   │
│   ├── camera/
│   │   ├── camera_service.py
│   │   └── camera_interface.py
│   │
│   ├── ui/
│   │   ├── window.py
│   │   ├── welcome_screen.py
│   │   ├── camera_screen.py
│   │   ├── countdown_screen.py
│   │   ├── review_screen.py
│   │   ├── processing_screen.py
│   │   ├── share_screen.py
│   │   └── error_screen.py
│   │
│   ├── session/
│   │   ├── session.py
│   │   └── session_manager.py
│   │
│   ├── processing/
│   │   ├── image_processor.py
│   │   ├── photo_strip.py
│   │   ├── filters.py
│   │   └── templates.py
│   │
│   ├── storage/
│   │   ├── storage_service.py
│   │   └── cleanup.py
│   │
│   ├── sharing/
│   │   ├── server.py
│   │   ├── qr_service.py
│   │   └── download_manager.py
│   │
│   └── hardware/
│       ├── button.py
│       ├── lighting.py
│       └── power.py
│
├── assets/
│   ├── icons/
│   ├── fonts/
│   ├── templates/
│   └── branding/
│
├── config/
│   └── config.yaml
│
├── scripts/
│   ├── install.sh
│   ├── start.sh
│   └── setup_service.sh
│
├── systemd/
│   └── photobooth.service
│
└── tests/
    ├── test_sessions.py
    ├── test_processing.py
    ├── test_storage.py
    └── test_sharing.py
```

---

# 8. Application State Machine

The application's flow should be explicitly represented as states.

```text
BOOTING
   │
   ▼
IDLE
   │
   ▼
PREVIEW
   │
   ▼
COUNTDOWN
   │
   ▼
CAPTURE
   │
   ├───────────────┐
   │               │
more photos      finished
   │               │
   ▼               ▼
COUNTDOWN       PROCESSING
                   │
                   ▼
                 REVIEW
                /      \
           RETAKE       KEEP
             │            │
             ▼            ▼
          PREVIEW        SHARE
                           │
                           ▼
                          IDLE
```

The state machine should prevent invalid operations.

For example, tapping the capture button multiple times during `COUNTDOWN` must not create multiple captures.

---

# 9. Camera Service

Camera functionality must be isolated in `CameraService`.

Responsibilities:

- Initialize camera
- Start live preview
- Stop live preview
- Trigger autofocus
- Capture high-resolution image
- Detect camera failures
- Attempt camera recovery
- Release camera resources

Example interface:

```python
class CameraService:

    def initialize(self):
        ...

    def start_preview(self):
        ...

    def autofocus(self):
        ...

    def capture(self, output_path):
        ...

    def stop_preview(self):
        ...

    def shutdown(self):
        ...
```

The UI should never communicate directly with Picamera2.

---

# 10. Photo Session Model

Every group of photos belongs to a `PhotoSession`.

Example:

```python
class PhotoSession:
    id: str
    created_at: datetime
    photos: list
    processed_photos: list
    strip_path: str | None
    share_token: str
```

Session IDs should use UUIDs or another collision-resistant identifier.

Example:

```text
8fa14c21
```

Do not use sequential IDs for externally accessible URLs.

---

# 11. Capture Flow

Default session:

```text
4 photographs
3-second countdown before each
```

Sequence:

```text
Start Session

3
2
1

short pause

3
2
1

short pause

3
2
1

short pause

3
2
1

Processing...
```

The number of photos and countdown duration must be configurable.

Example:

```yaml
session:
  photos_per_session: 4
  countdown_seconds: 3
  delay_between_photos_ms: 1000
```

---

# 12. Image Processing

Image processing should happen **after capture**, not continuously during live preview.

Pipeline:

```text
Original Image
      ↓
Orientation Correction
      ↓
Crop
      ↓
Resize
      ↓
Basic Color Adjustment
      ↓
Optional Filter
      ↓
Template / Overlay
      ↓
Processed Image
```

Always preserve original captures.

Do not destructively modify original images.

Use Pillow for most processing.

Only introduce OpenCV when Pillow cannot reasonably perform the required operation.

---

# 13. Photo Strip Generation

The application should generate a traditional vertical photo strip from the captured images.

Example:

```text
┌──────────────────┐
│                  │
│     PHOTO 1      │
│                  │
├──────────────────┤
│                  │
│     PHOTO 2      │
│                  │
├──────────────────┤
│                  │
│     PHOTO 3      │
│                  │
├──────────────────┤
│                  │
│     PHOTO 4      │
│                  │
├──────────────────┤
│                  │
│    EVENT NAME    │
│    09.14.2026    │
│                  │
└──────────────────┘
```

Templates should be data-driven rather than hardcoded.

Possible future templates:

```text
classic
wedding
birthday
graduation
holiday
custom_event
```

---

# 14. File Storage

Recommended structure:

```text
photos/
└── 2026-09-14/
    └── <session_uuid>/
        │
        ├── originals/
        │   ├── 01.jpg
        │   ├── 02.jpg
        │   ├── 03.jpg
        │   └── 04.jpg
        │
        ├── processed/
        │   ├── 01.jpg
        │   ├── 02.jpg
        │   ├── 03.jpg
        │   └── 04.jpg
        │
        └── strip.jpg
```

Storage must:

- never overwrite another session
- preserve originals
- monitor available disk space
- gracefully handle full storage
- support future removable USB storage
- avoid excessive SD-card writes

---

# 15. Local Photo Sharing

A core requirement is **offline QR-based sharing**.

The Pi should run a lightweight local HTTP server.

Example:

```text
http://photobooth.local/s/8fa14c21
```

The resulting page should display:

```text
YOUR PHOTOS

[ Photo 1 ]

[ Photo 2 ]

[ Photo 3 ]

[ Photo 4 ]

[ Photo Strip ]

[ DOWNLOAD ALL ]
```

The booth UI should generate a QR code pointing to this session URL.

---

# 16. Offline Networking

The final system should not depend on venue Wi-Fi.

Preferred final architecture:

```text
                 Raspberry Pi
                      │
                Wi-Fi Hotspot
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
      Phone         Phone         Phone
```

The Pi should eventually operate as its own Wi-Fi access point.

Example SSID:

```text
PhotoBooth
```

Users connect locally and retrieve photos directly from the Pi.

Internet access should not be required.

Hotspot configuration is a later milestone and should not block initial application development.

---

# 17. Sharing Security

Photo URLs must not use predictable sequential IDs.

Use randomly generated tokens.

Example:

```text
/s/a8F3kmP2xQ
```

instead of:

```text
/session/42
```

Requirements:

- random session tokens
- no directory listing
- sessions isolated from one another
- user cannot modify URL to trivially access another session
- optional expiration support
- no remote administrative endpoints exposed publicly

The local system does not need enterprise-level authentication, but reasonable privacy protections should be implemented.

---

# 18. UI Requirements

The interface should be optimized for:

```text
7" touchscreen
720 × 1280
portrait orientation
```

Requirements:

- fullscreen
- large touch targets
- minimal text
- high readability
- no desktop chrome
- no mouse cursor
- no keyboard requirement
- clear progress indicators
- clear error states
- responsive touch input

Primary screens:

```text
Welcome
Camera
Countdown
Processing
Review
Share
Error
```

---

# 19. Welcome Screen

Example:

```text
┌──────────────────────┐
│                      │
│      PHOTO BOOTH     │
│                      │
│         ◉            │
│                      │
│                      │
│    TAP TO START      │
│                      │
│                      │
└──────────────────────┘
```

The application should automatically return here after inactivity.

---

# 20. Camera Screen

Example:

```text
┌──────────────────────┐
│                      │
│                      │
│     LIVE PREVIEW     │
│                      │
│                      │
│                      │
│                      │
│   ┌──────────────┐   │
│   │ TAKE PHOTOS  │   │
│   └──────────────┘   │
│                      │
└──────────────────────┘
```

---

# 21. Countdown

Countdown should be extremely obvious:

```text
┌──────────────────────┐
│                      │
│                      │
│                      │
│          3           │
│                      │
│                      │
│                      │
└──────────────────────┘
```

Then:

```text
3 → 2 → 1 → FLASH → CAPTURE
```

Animations must remain lightweight enough for the Pi 3.

---

# 22. Physical Capture Button

Optional GPIO button:

```text
GPIO17 ───── Button ───── GND
```

The physical button should call the same application event as the touchscreen capture button.

Do not create separate capture logic.

Conceptually:

```python
start_button_pressed()
        │
        ▼
session_manager.start_session()
```

Both:

```text
Touch Button ─────┐
                  ├── start_session()
GPIO Button ──────┘
```

---

# 23. Lighting

Lighting should be treated as its own hardware service.

```python
class LightingService:

    def idle(self):
        ...

    def preview(self):
        ...

    def countdown(self):
        ...

    def capture(self):
        ...

    def off(self):
        ...
```

This allows future integration with controllable LEDs without affecting application logic.

---

# 24. Configuration

Avoid hardcoded user-adjustable values.

Example:

```yaml
booth:
  name: "Photo Booth"

session:
  photos_per_session: 4
  countdown_seconds: 3

camera:
  resolution_width: 4608
  resolution_height: 2592
  autofocus: true

display:
  fullscreen: true
  orientation: portrait

storage:
  path: "/home/pi/photobooth/photos"
  minimum_free_space_mb: 1000

sharing:
  enabled: true
  hostname: "photobooth.local"
  port: 8080

hardware:
  physical_button: true
  button_gpio: 17
```

---

# 25. Error Handling

The application must never expose raw Python exceptions to booth users.

Examples:

### Camera unavailable

```text
Camera Error

We're having trouble with the camera.

Retrying...
```

### Storage full

```text
Photo Booth Temporarily Unavailable

Storage needs attention.
```

### Sharing unavailable

Photo capture should still work.

```text
Your photos were saved successfully.

QR sharing is temporarily unavailable.
```

Sharing failure should **not destroy an otherwise successful photo session**.

---

# 26. Recovery

The booth should recover automatically whenever practical.

Example:

```text
Camera Failure
      ↓
Retry
      ↓
Retry
      ↓
Retry
      ↓
Restart Camera Service
      ↓
Still Failed
      ↓
Display Friendly Error
```

Subsystem failures should not necessarily terminate the entire application.

---

# 27. Logging

Use Python's logging framework.

Example:

```text
logs/
└── photobooth.log
```

Log:

- application startup
- shutdown
- session creation
- successful capture
- processing time
- camera errors
- storage errors
- server errors
- hardware errors

Do not log private session URLs unnecessarily.

Implement log rotation to prevent unlimited disk usage.

---

# 28. Automatic Startup

The final application should run through `systemd`.

```text
Power On
   ↓
Linux Boot
   ↓
photobooth.service
   ↓
Python Application
   ↓
Fullscreen UI
```

Example service:

```ini
[Unit]
Description=Portable Photo Booth
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/photobooth
ExecStart=/home/pi/photobooth/.venv/bin/python -m app.main
Restart=always
RestartSec=3
User=pi

[Install]
WantedBy=multi-user.target
```

The exact configuration may need adjustment depending on how the graphical session is configured.

---

# 29. Graceful Shutdown

Do not encourage users to disconnect battery power while Linux is running.

Provide a safe shutdown mechanism.

Possible approaches:

- hidden admin touchscreen control
- long press of physical button
- dedicated power button

Flow:

```text
Shutdown Requested
       ↓
Stop New Sessions
       ↓
Finish Disk Writes
       ↓
Stop Web Server
       ↓
Release Camera
       ↓
Turn Off LEDs
       ↓
Linux Shutdown
```

---

# 30. Performance Requirements

Target:

```text
Application launch:      < 15 seconds after OS ready
Touch response:          < 150 ms
Countdown:               smooth
Capture delay:           < 2 seconds
Photo processing:        < 10 seconds/session
QR generation:           < 2 seconds
```

These are targets rather than strict guarantees.

Optimize for perceived responsiveness.

Never block the main UI thread with:

- image processing
- disk operations
- network operations
- long camera operations

Use worker threads where appropriate.

---

# 31. Resource Management

Because the target is a Pi 3:

- Do not keep unnecessary full-resolution images in RAM.
- Load images only when needed.
- Resize previews before displaying them.
- Release camera buffers.
- Avoid unnecessary copies.
- Close files immediately.
- Avoid memory leaks across sessions.

The booth should be capable of running for several hours without restarting.

---

# 32. Admin Mode

Eventually provide a hidden admin interface.

Possible entry:

```text
Press booth logo for 5 seconds
```

Admin features:

```text
Storage Remaining
Battery Status
Camera Status
Network Status
Session Count

[ Change Event ]
[ Change Template ]
[ Gallery ]
[ Export Photos ]
[ Restart App ]
[ Shutdown ]
```

Admin functionality is not required for the initial MVP.

---

# 33. Development Mode

The project should support development without Raspberry Pi hardware.

Services should use interfaces so mock implementations can be substituted.

Example:

```text
CameraInterface
      │
 ┌────┴─────┐
 │          │
 ▼          ▼
PiCamera   MockCamera
```

On a developer computer, `MockCamera` can return sample photographs.

Likewise:

```text
LightingInterface
     │
 ┌───┴────┐
 ▼        ▼
GPIO     Mock
```

This allows most application development and automated testing without the Pi connected.

---

# 34. Testing

Tests should cover at minimum:

### Session

- session creation
- unique IDs
- photo count
- session completion

### Storage

- directory creation
- filename collision prevention
- low disk-space detection

### Processing

- resizing
- cropping
- strip generation
- original preservation

### Sharing

- token generation
- correct session retrieval
- invalid token rejection

### State Machine

Ensure invalid transitions cannot occur.

Example:

```text
IDLE → CAPTURE
```

should not be possible without starting a session.

---

# 35. MVP Scope

The initial MVP should include only:

1. Application launches fullscreen.
2. Welcome screen.
3. Live camera preview.
4. Start photo session.
5. 3-second countdown.
6. Capture four photos.
7. Save originals.
8. Generate processed photos.
9. Generate photo strip.
10. Display finished strip.
11. Generate QR code.
12. Local webpage for downloading photos.
13. Return to welcome screen.
14. Recover from basic errors.

Do **not** build advanced features before the MVP works reliably.

---

# 36. Explicitly Out of Scope for MVP

Do not initially implement:

- AI background removal
- facial recognition
- cloud accounts
- online gallery
- payment processing
- analytics
- remote management
- social-media APIs
- video
- GIFs
- boomerangs
- printer support
- complex filters
- multi-booth synchronization
- mobile application

These are future features.

---

# 37. Development Milestones

## Milestone 1 — Camera

Goal:

```text
Launch application
→ display camera
→ countdown
→ capture image
→ save image
```

No touchscreen-specific UI required.

---

## Milestone 2 — Booth UI

Implement:

```text
Welcome
↓
Preview
↓
Countdown
↓
Capture
↓
Review
```

Application should run fullscreen.

---

## Milestone 3 — Sessions

Implement four-photo sessions.

```text
Start
↓
Photo 1
↓
Photo 2
↓
Photo 3
↓
Photo 4
↓
Complete
```

---

## Milestone 4 — Processing

Implement:

- cropping
- resizing
- processed copies
- photo strip generation

---

## Milestone 5 — QR Sharing

Implement:

```text
Session
↓
Random Share Token
↓
Local HTTP Page
↓
QR Code
↓
Phone Download
```

Initially assume the Pi and phone share the same Wi-Fi network.

---

## Milestone 6 — Touchscreen

Optimize interface for:

```text
720 × 1280 portrait
```

Verify all functionality without keyboard/mouse.

---

## Milestone 7 — Offline Hotspot

Configure Pi to provide its own Wi-Fi network.

Goal:

```text
No Internet
No Router
No Venue Wi-Fi

Photo Booth
     ↓
creates Wi-Fi
     ↓
Guest connects
     ↓
QR opens locally
     ↓
Guest downloads photos
```

---

## Milestone 8 — Hardware Integration

Add:

- physical button
- lighting controls
- battery
- shutdown mechanism

---

## Milestone 9 — Kiosk Deployment

Configure:

- automatic startup
- fullscreen UI
- hidden desktop
- service restart
- log rotation
- graceful shutdown

The device should behave like an appliance.

---

## Milestone 10 — Reliability

Test:

- 100+ consecutive sessions
- Wi-Fi loss
- camera disconnect
- low storage
- server failure
- repeated touch input
- user abandonment
- unexpected application crash
- long runtime
- thermal behavior
- low battery
- restart recovery

---

# 38. Future Roadmap

Once the MVP is stable:

```text
V1
├── Photos
├── Touch UI
├── Photo strips
├── Local QR sharing
└── Portable operation

V2
├── Filters
├── Custom themes
├── Event branding
├── GIFs
└── Boomerangs

V3
├── Physical printer
├── Admin dashboard
├── Event galleries
├── USB export
└── Cloud backup

V4
├── Remote configuration
├── Multiple booths
├── Event accounts
├── Analytics
└── Commercial deployment
```

---

# 39. Engineering Principles

When making implementation decisions, prioritize in this order:

```text
1. Reliability
2. User experience
3. Simplicity
4. Performance
5. Maintainability
6. Extensibility
7. Additional features
```

Do not sacrifice reliability to add features.

Prefer simple solutions that work consistently on the Pi 3 over sophisticated architectures designed for more powerful hardware.

---

# 40. Definition of Done

The MVP is complete when a nontechnical person can:

1. Turn on the booth.
2. Wait for it to boot.
3. Tap Start.
4. See themselves in the camera.
5. Take four timed photographs.
6. See the completed photo strip.
7. Scan a QR code.
8. Download their photos to their phone.
9. Finish the session.
10. Allow the next person to immediately use the booth.

All of this must work:

**without a keyboard, mouse, laptop, internet connection, or external router.**

The final product should behave as a **self-contained portable photo booth appliance**, not as a Raspberry Pi development environment.