import 'package:json_annotation/json_annotation.dart';

part 'assignment.g.dart';

@JsonSerializable()
class Assignment {
  final String id;
  final String title;
  final String? description;
  @JsonKey(name: 'assignment_type')
  final String assignmentType;
  @JsonKey(name: 'type_display')
  final String typeDisplay;
  @JsonKey(name: 'subject_name')
  final String subjectName;
  @JsonKey(name: 'class_name')
  final String? className;
  @JsonKey(name: 'assigned_date')
  final String assignedDate;
  @JsonKey(name: 'due_date')
  final String dueDate;
  @JsonKey(name: 'max_marks')
  final int maxMarks;
  @JsonKey(name: 'is_overdue')
  final bool isOverdue;
  @JsonKey(name: 'submission_status')
  final Map<String, dynamic>? submissionStatus;

  Assignment({
    required this.id,
    required this.title,
    this.description,
    required this.assignmentType,
    required this.typeDisplay,
    required this.subjectName,
    this.className,
    required this.assignedDate,
    required this.dueDate,
    required this.maxMarks,
    required this.isOverdue,
    this.submissionStatus,
  });

  bool get isSubmitted => submissionStatus?['submitted'] ?? false;
  String? get status => submissionStatus?['status'];

  factory Assignment.fromJson(Map<String, dynamic> json) => _$AssignmentFromJson(json);
  Map<String, dynamic> toJson() => _$AssignmentToJson(this);
}
