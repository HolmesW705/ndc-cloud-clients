# NDC Cloud clients

Northern Data Centre's branded desktop, Android and iPhone/iPad client source.
Customer service: https://cloud.northerndatacenter.net/settings/help

This repository contains the exact source patches, independent application
identities, and build workflow. It contains no customer data, credentials,
signing keys or production infrastructure configuration.

## Reconstruct source

Use Python 3 and Git. Choose a new destination for each command.

```sh
python3 prepare.py desktop desktop
python3 prepare.py android android
python3 prepare.py ios ios
```

`prepare.py` fetches and verifies the pinned upstream commit, then applies the
complete NDC patch including binary assets. It never overwrites existing source.
Upstream build instructions and license notices remain in each source checkout.

## Build and release

- Android: JDK 21, Android SDK 37.0, NDK 29.0.14206865 and CMake 4.1.2.
  Run `./gradlew :app:assembleGenericRelease` in the prepared Android source.
  The result must be signed with NDC's private release key before distribution.
- iOS/iPadOS: use Xcode 27.2 or newer. Set NDC's Apple Team ID for all targets,
  register the app identifiers and groups in `identities.json`, then archive
  the `Nextcloud` scheme. Keep Swift packages under DerivedData/SourcePackages;
  the upstream extension header-search paths depend on that location.
- Desktop: follow `doc/macOS-development.md` or the CMake instructions in the
  prepared source. Windows and Linux packages use the upstream KDE Craft and
  AppImage build environments in the manually dispatched workflow.

Unsigned build artifacts are build outputs, not approved customer releases.
Apple notarization/App Store distribution and Windows signing require NDC's
publisher credentials. Automatic upstream-client updates are disabled in this
independently identified fork; NDC must publish and maintain its own updates.

## Licenses and credit

These are modified Nextcloud clients, not software authored entirely by NDC.
The desktop is GPL-2.0-or-later, Android is AGPL-3.0-or-later with retained
per-file notices, and iOS is GPL-3.0-or-later with its Apple App Store exception.
The complete upstream license and attribution files are in each reconstructed
source tree. Inter is bundled under its SIL Open Font License. NDC names and
logos are Northern Data Centre trademarks; this repository does not grant a
trademark license. Corresponding source for a distributed release is its pinned
upstream source plus the exact NDC patch in that release.
