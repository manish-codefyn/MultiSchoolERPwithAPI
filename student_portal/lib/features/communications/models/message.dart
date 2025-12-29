import 'package:json_annotation/json_annotation.dart';

part 'message.g.dart';

@JsonSerializable()
class Message {
  final String id;
  @JsonKey(name: 'sender_name')
  final String senderName;
  final String text;
  @JsonKey(name: 'sent_at')
  final String sentAt;
  @JsonKey(name: 'is_me')
  final bool isMe;

  Message({
    required this.id,
    required this.senderName,
    required this.text,
    required this.sentAt,
    required this.isMe,
  });

  factory Message.fromJson(Map<String, dynamic> json) => _$MessageFromJson(json);
  Map<String, dynamic> toJson() => _$MessageToJson(this);
}

@JsonSerializable()
class MessageThread {
  final String id;
  @JsonKey(name: 'other_participant')
  final String otherParticipant;
  @JsonKey(name: 'last_message')
  final String? lastMessage;
  @JsonKey(name: 'updated_at')
  final String updatedAt;
  @JsonKey(name: 'unread_count')
  final int unreadCount;

  MessageThread({
    required this.id,
    required this.otherParticipant,
    this.lastMessage,
    required this.updatedAt,
    required this.unreadCount,
  });

  factory MessageThread.fromJson(Map<String, dynamic> json) => _$MessageThreadFromJson(json);
  Map<String, dynamic> toJson() => _$MessageThreadToJson(this);
}
