/** @file
*
*  Copyright (c) 2013, ARM Limited. All rights reserved.
*
*  This program and the accompanying materials
*  are licensed and made available under the terms and conditions of the BSD License
*  which accompanies this distribution.  The full text of the license may be found at
*  http://opensource.org/licenses/bsd-license.php
*
*  THE PROGRAM IS DISTRIBUTED UNDER THE BSD LICENSE ON AN "AS IS" BASIS,
*  WITHOUT WARRANTIES OR REPRESENTATIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED.
*
**/

#include "ArmVExpressInternal.h"

#include <Protocol/BlockIo.h>

#include <Library/BaseMemoryLib.h>

#define DRAM_SIGNATURE                SIGNATURE_32('d', 'r', 'a', 'm')

typedef struct {
  UINT32                              Signature;
  EFI_HANDLE                          Handle;

  EFI_BLOCK_IO_PROTOCOL               BlockIoProtocol;
  EFI_BLOCK_IO_MEDIA                  Media;

  struct {
    VENDOR_DEVICE_PATH                Vendor;
    EFI_DEVICE_PATH_PROTOCOL          End;
  }                                   DevicePath;
} DRAM_INSTANCE;

#define INSTANCE_FROM_BLKIO_THIS(a)   CR(a, DRAM_INSTANCE, BlockIoProtocol, DRAM_SIGNATURE)

//
// BlockIO Protocol function EFI_BLOCK_IO_PROTOCOL.Reset
//
EFI_STATUS
EFIAPI
DramBlockIoReset (
  IN EFI_BLOCK_IO_PROTOCOL    *This,
  IN BOOLEAN                  ExtendedVerification
  )
{
  ASSERT (0);
  return EFI_UNSUPPORTED;
}

//
// BlockIO Protocol function EFI_BLOCK_IO_PROTOCOL.ReadBlocks
//
EFI_STATUS
EFIAPI
DramBlockIoReadBlocks (
  IN  EFI_BLOCK_IO_PROTOCOL   *This,
  IN  UINT32                  MediaId,
  IN  EFI_LBA                 Lba,
  IN  UINTN                   BufferSizeInBytes,
  OUT VOID                    *Buffer
  )
{
  DRAM_INSTANCE *Instance;

  // The instance and buffer pointers must be valid
  if ((This == NULL) || (Buffer == NULL)) {
    return EFI_INVALID_PARAMETER;
  }

  // We must have some bytes to read
  if (BufferSizeInBytes == 0) {
    return EFI_BAD_BUFFER_SIZE;
  }

  // Check the instance is ours
  Instance = INSTANCE_FROM_BLKIO_THIS (This);
  if (Instance->Signature != DRAM_SIGNATURE) {
    return EFI_INVALID_PARAMETER;
  }

  // The size of the buffer must be a multiple of the block size
  if ((BufferSizeInBytes % Instance->Media.BlockSize) != 0) {
    return EFI_BAD_BUFFER_SIZE;
  }

  CopyMem (Buffer, (VOID*)((UINTN)FixedPcdGet64 (PcdSystemMemoryBase) + (UINTN)Lba), BufferSizeInBytes);
  return EFI_SUCCESS;
}

//
// BlockIO Protocol function EFI_BLOCK_IO_PROTOCOL.WriteBlocks
//
EFI_STATUS
EFIAPI
DramBlockIoWriteBlocks (
  IN  EFI_BLOCK_IO_PROTOCOL   *This,
  IN  UINT32                  MediaId,
  IN  EFI_LBA                 Lba,
  IN  UINTN                   BufferSizeInBytes,
  IN  VOID                    *Buffer
  )
{
  ASSERT (0);
  return EFI_UNSUPPORTED;
}

//
// BlockIO Protocol function EFI_BLOCK_IO_PROTOCOL.FlushBlocks
//
EFI_STATUS
EFIAPI
DramBlockIoFlushBlocks (
  IN EFI_BLOCK_IO_PROTOCOL    *This
  )
{
  ASSERT (0);
  return EFI_UNSUPPORTED;
}

STATIC DRAM_INSTANCE mDramInstance = {
  DRAM_SIGNATURE, // Signature
  NULL,           // Handle

  {
    EFI_BLOCK_IO_PROTOCOL_REVISION2, // Revision
    NULL, // Media ... NEED TO BE FILLED
    DramBlockIoReset, // Reset;
    DramBlockIoReadBlocks,          // ReadBlocks
    DramBlockIoWriteBlocks,         // WriteBlocks
    DramBlockIoFlushBlocks          // FlushBlocks
  }, // BlockIoProtocol

  {
    0, // MediaId
    FALSE, // RemovableMedia
    TRUE, // MediaPresent
    FALSE, // LogicalPartition
    TRUE, // ReadOnly
    FALSE, // WriteCaching;
    0x1, // BlockSize
    4, //  IoAlign
    FixedPcdGet64 (PcdSystemMemorySize), // LastBlock
    0, // LowestAlignedLba
    1, // LogicalBlocksPerPhysicalBlock
  }, //Media;

  {
    {
      {
        HARDWARE_DEVICE_PATH,
        HW_VENDOR_DP,
        { (UINT8)(sizeof (VENDOR_DEVICE_PATH)), (UINT8)((sizeof (VENDOR_DEVICE_PATH)) >> 8) },
      },
      // 30f57e4a-69ce-4fb7-b7a1-4c7ce49d57a6
      { 0x30f57e4a, 0x69ce, 0x4fb7, { 0xb7, 0xa1, 0x4c, 0x7c, 0xe4, 0x9d, 0x57, 0xa6 } },
    },
    {
      END_DEVICE_PATH_TYPE,
      END_ENTIRE_DEVICE_PATH_SUBTYPE,
      { sizeof (EFI_DEVICE_PATH_PROTOCOL), 0 }
    }
  } // DevicePath
};

EFI_STATUS
InitDramBlockIo (
  VOID
  )
{
  EFI_STATUS Status;

  // Initialize instance
  mDramInstance.BlockIoProtocol.Media = &mDramInstance.Media;

  Status = gBS->InstallMultipleProtocolInterfaces (
                  &mDramInstance.Handle,
                  &gEfiDevicePathProtocolGuid, &mDramInstance.DevicePath,
                  &gEfiBlockIoProtocolGuid,  &mDramInstance.BlockIoProtocol,
                  NULL
                  );

  return Status;
}

