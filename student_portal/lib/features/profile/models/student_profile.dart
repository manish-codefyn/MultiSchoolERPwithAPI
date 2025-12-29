import 'package:json_annotation/json_annotation.dart';

part 'student_profile.g.dart';

@JsonSerializable()
class StudentProfile {
  final String id;
  @JsonKey(name: 'admission_number')
  final String? admissionNumber;
  @JsonKey(name: 'roll_number')
  final String? rollNumber;
  @JsonKey(name: 'first_name')
  final String firstName;
  @JsonKey(name: 'middle_name')
  final String? middleName;
  @JsonKey(name: 'last_name')
  final String? lastName;
  @JsonKey(name: 'full_name')
  final String fullName;
  @JsonKey(name: 'date_of_birth')
  final String? dateOfBirth;
  final int? age;
  final String? gender;
  @JsonKey(name: 'blood_group')
  final String? bloodGroup;
  @JsonKey(name: 'personal_email')
  final String? email;
  @JsonKey(name: 'mobile_primary')
  final String? phone;
  @JsonKey(name: 'current_class_name')
  final String? className;
  @JsonKey(name: 'section_name')
  final String? sectionName;
  @JsonKey(name: 'photo_url')
  final String? photoUrl;
  final String status;

  StudentProfile({
    required this.id,
    this.admissionNumber,
    this.rollNumber,
    required this.firstName,
    this.middleName,
    this.lastName,
    required this.fullName,
    this.dateOfBirth,
    this.age,
    this.gender,
    this.bloodGroup,
    this.email,
    this.phone,
    this.className,
    this.sectionName,
    this.photoUrl,
    required this.status,
  });

  factory StudentProfile.fromJson(Map<String, dynamic> json) => _$StudentProfileFromJson(json);
  Map<String, dynamic> toJson() => _$StudentProfileToJson(this);
}
