import 'package:json_annotation/json_annotation.dart';

part 'hostel.g.dart';

@JsonSerializable()
class Hostel {
  final String id;
  final String name;
  final String code;
  @JsonKey(name: 'hostel_type')
  final String hostelType;
  @JsonKey(name: 'type_display')
  final String typeDisplay;
  final String? address;

  Hostel({
    required this.id,
    required this.name,
    required this.code,
    required this.hostelType,
    required this.typeDisplay,
    this.address,
  });

  factory Hostel.fromJson(Map<String, dynamic> json) => _$HostelFromJson(json);
  Map<String, dynamic> toJson() => _$HostelToJson(this);
}

@JsonSerializable()
class HostelRoom {
  final String id;
  @JsonKey(name: 'room_number')
  final String roomNumber;
  final String floor;
  @JsonKey(name: 'room_type')
  final String roomType;
  @JsonKey(name: 'type_display')
  final String typeDisplay;
  final int capacity;

  HostelRoom({
    required this.id,
    required this.roomNumber,
    required this.floor,
    required this.roomType,
    required this.typeDisplay,
    required this.capacity,
  });

  factory HostelRoom.fromJson(Map<String, dynamic> json) => _$HostelRoomFromJson(json);
  Map<String, dynamic> toJson() => _$HostelRoomToJson(this);
}

@JsonSerializable()
class HostelAllocation {
  final String id;
  @JsonKey(name: 'hostel_details')
  final Hostel hostelDetails;
  @JsonKey(name: 'room_details')
  final HostelRoom roomDetails;
  @JsonKey(name: 'allocation_date')
  final String allocationDate;
  final String status;
  @JsonKey(name: 'status_display')
  final String statusDisplay;
  @JsonKey(name: 'is_active')
  final bool isActive;
  @JsonKey(name: 'bed_number')
  final String? bedNumber;

  HostelAllocation({
    required this.id,
    required this.hostelDetails,
    required this.roomDetails,
    required this.allocationDate,
    required this.status,
    required this.statusDisplay,
    required this.isActive,
    this.bedNumber,
  });

  factory HostelAllocation.fromJson(Map<String, dynamic> json) => _$HostelAllocationFromJson(json);
  Map<String, dynamic> toJson() => _$HostelAllocationToJson(this);
}

@JsonSerializable()
class HostelAttendance {
  final String id;
  final String date;
  final String status;
  @JsonKey(name: 'status_display')
  final String statusDisplay;
  final String? remarks;

  HostelAttendance({
    required this.id,
    required this.date,
    required this.status,
    required this.statusDisplay,
    this.remarks,
  });

  factory HostelAttendance.fromJson(Map<String, dynamic> json) => _$HostelAttendanceFromJson(json);
  Map<String, dynamic> toJson() => _$HostelAttendanceToJson(this);
}

@JsonSerializable()
class Roommate {
  final String id;
  @JsonKey(name: 'full_name')
  final String fullName;
  @JsonKey(name: 'class')
  final String? className;
  @JsonKey(name: 'photo_url')
  final String? photoUrl;

  Roommate({
    required this.id,
    required this.fullName,
    this.className,
    this.photoUrl,
  });

  factory Roommate.fromJson(Map<String, dynamic> json) => _$RoommateFromJson(json);
  Map<String, dynamic> toJson() => _$RoommateToJson(this);
}

@JsonSerializable()
class HostelDetails {
  final HostelAllocation? allocation;
  final List<Roommate> roommates;
  @JsonKey(name: 'attendance_history')
  final List<HostelAttendance> attendanceHistory;

  HostelDetails({
    this.allocation,
    required this.roommates,
    required this.attendanceHistory,
  });

  factory HostelDetails.fromJson(Map<String, dynamic> json) => _$HostelDetailsFromJson(json);
  Map<String, dynamic> toJson() => _$HostelDetailsToJson(this);
}
