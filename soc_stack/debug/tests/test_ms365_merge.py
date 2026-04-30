#!/usr/bin/env python3

"""
Test MS365 data merging.
"""

import json

from soc_stack.scanners.ms365_aggregator import Microsoft365Aggregator
from soc_stack.scanners.intune_scanner import IntuneScanner
from soc_stack.scanners.teams_scanner import TeamsScanner
from soc_stack.scanners.entra_scanner import EntraScanner

def ms365_merge_tester():

    print("--- Starting Microsoft 365 Merge Debug Test ---")

    intune_asset_raw_sample = {
        "id": "734482e2-bec7-47ba-bd51-4897355f2766",
        "userId": "f74d0f00-ac95-4725-8241-d8f0527cc06a",
        "deviceName": "kantine_AndroidAOSP_5/1/2025_2:56 PM",
        "managedDeviceOwnerType": "company",
        "managementState": "managed",
        "enrolledDateTime": "2025-05-01T14:56:21Z",
        "lastSyncDateTime": "2025-11-13T04:19:59Z",
        "operatingSystem": "Android",
        "complianceState": "compliant",
        "jailBroken": "Unknown",
        "managementAgent": "intuneAosp",
        "osVersion": "10",
        "easActivated": False,
        "easDeviceId": "",
        "easActivationDateTime": "0001-01-01T00:00:00Z",
        "azureADRegistered": True,
        "deviceEnrollmentType": "androidAOSPUserOwnedDeviceEnrollment",
        "activationLockBypassCode": None,
        "emailAddress": "kantine@diabetes.dk",
        "azureADDeviceId": "cc486eb9-8c93-462a-bb0f-adcef7d50e88",
        "deviceRegistrationState": "registered",
        "deviceCategoryDisplayName": "Unknown",
        "isSupervised": False,
        "exchangeLastSuccessfulSyncDateTime": "0001-01-01T00:00:00Z",
        "exchangeAccessState": "none",
        "exchangeAccessStateReason": "none",
        "remoteAssistanceSessionUrl": None,
        "remoteAssistanceSessionErrorDetails": None,
        "isEncrypted": True,
        "userPrincipalName": "kantine@diabetes.dk",
        "model": "RoomPanel",
        "manufacturer": "Yealink",
        "imei": "",
        "complianceGracePeriodExpirationDateTime": "9999-12-31T23:59:59Z",
        "serialNumber": "803110D072402058",
        "phoneNumber": "",
        "androidSecurityPatchLevel": "2023-06-05",
        "userDisplayName": "Kantine",
        "configurationManagerClientEnabledFeatures": None,
        "wiFiMacAddress": "",
        "deviceHealthAttestationState": None,
        "subscriberCarrier": "",
        "meid": "",
        "totalStorageSpaceInBytes": 8709472256,
        "freeStorageSpaceInBytes": 0,
        "managedDeviceName": "kantine_AndroidAOSP_5/1/2025_2:56 PM",
        "partnerReportedThreatState": "unknown",
        "requireUserEnrollmentApproval": None,
        "managementCertificateExpirationDate": "2026-05-01T00:59:41Z",
        "iccid": None,
        "udid": None,
        "notes": None,
        "ethernetMacAddress": None,
        "physicalMemoryInBytes": 0,
        "enrollmentProfileName": None,
        "deviceActionResults": []
        }

    teams_asset_raw_sample = {
        "id": "16ca4848-f909-4090-b11d-59eabeacfff2",
        "deviceType": "teamsPanel",
        "notes": None,
        "companyAssetTag": None,
        "healthStatus": "nonUrgent",
        "activityState": "unknown",
        "createdDateTime": "2022-03-23T07:44:27Z",
        "lastModifiedDateTime": "2026-01-23T17:03:50Z",
        "createdBy": None,
        "hardwareDetail": {
            "serialNumber": "803110d072402058",
            "uniqueId": "803110d072402058",
            "macAddresses": [
            "ETHERNET:805EC066FDA6"
            ],
            "manufacturer": "yealink",
            "model": "roompanel"
        },
        "lastModifiedBy": {
            "application": None,
            "device": None,
            "user": {
            "@odata.type": "#microsoft.graph.teamworkUserIdentity",
            "id": "6fd71709-58ef-4661-ae77-1d11be72dce9",
            "displayName": "Michael Damgaard Larsen",
            "userIdentityType": "aadUser"
            }
        },
        "currentUser": {
            "id": "f74d0f00-ac95-4725-8241-d8f0527cc06a",
            "displayName": "Kantine",
            "userIdentityType": "aadUser"
        }
        } 
    
    entra_asset_raw_sample = {
        "id": "74ac9f62-40ab-4fb5-a881-2acd0778555e",
        "deviceId": "cc486eb9-8c93-462a-bb0f-adcef7d50e88",
        "displayName": "kantine_AndroidAOSP_5/1/2025_2:56 PM",
        "accountEnabled": True,
        "trustType": "Workplace",
        "profileType": "RegisteredDevice",
        "isCompliant": True,
        "isManaged": True,
        "approximateLastSignInDateTime": "2026-01-19T17:46:54Z",
        "registrationDateTime": "2022-03-08T06:53:19Z",
        "onPremisesSyncEnabled": None,
        "onPremisesLastSyncDateTime": None,
        "operatingSystem": "AndroidAOSP",
        "operatingSystemVersion": "10",
        "manufacturer": "Yealink",
        "model": "RoomPanel",
        "mdmAppId": "0000000a-0000-0000-c000-000000000000"
        }
         

    intune_scanner = IntuneScanner()
    teams_scanner = TeamsScanner()
    entra_scanner = EntraScanner()
    ms365_sync = Microsoft365Aggregator()

    transformed_raw_intune = intune_scanner.normalize_asset(intune_asset_raw_sample)
    print("\n--- Transformed Intune Asset ---")
    print(json.dumps(transformed_raw_intune, indent=2))
    print("--- End of Transformed Intune Asset ---")
    
    transformed_raw_teams = teams_scanner.normalize_asset(teams_asset_raw_sample)
    print("\n--- Transformed Teams Asset ---")
    print(json.dumps(transformed_raw_teams, indent=2))
    print("--- End of Transformed Teams Asset ---")
    
    transformed_raw_entra = entra_scanner.normalize_asset(entra_asset_raw_sample)
    print("\n--- Transformed Entra Asset ---")
    print(json.dumps(transformed_raw_entra, indent=2))
    print("--- End of Transformed Entra Asset ---")

    merged_asset = ms365_sync.merge_data(intune_data=[transformed_raw_intune], teams_data=[transformed_raw_teams], entra_data=[transformed_raw_entra])

    print("\n--- Final Merged Asset ---")
    print(json.dumps(merged_asset, indent=2))
    print("--- End of Test ---")

if __name__ == "__main__":
    ms365_merge_tester()
