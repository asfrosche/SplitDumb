import 'package:json_annotation/json_annotation.dart';
import 'user.dart';

part 'group.g.dart';

@JsonSerializable()
class Group {
  final int id;
  final String name;
  @JsonKey(name: 'created_by_user_id')
  final int createdByUserId;
  @JsonKey(name: 'default_currency')
  final String defaultCurrency;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  final List<GroupMember> members;

  Group({
    required this.id,
    required this.name,
    required this.createdByUserId,
    required this.defaultCurrency,
    required this.createdAt,
    required this.members,
  });

  factory Group.fromJson(Map<String, dynamic> json) => _$GroupFromJson(json);
  Map<String, dynamic> toJson() => _$GroupToJson(this);
}

@JsonSerializable()
class GroupMember {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  final String role;
  @JsonKey(name: 'joined_at')
  final DateTime joinedAt;
  final User user;

  GroupMember({
    required this.id,
    required this.userId,
    required this.role,
    required this.joinedAt,
    required this.user,
  });

  factory GroupMember.fromJson(Map<String, dynamic> json) => _$GroupMemberFromJson(json);
  Map<String, dynamic> toJson() => _$GroupMemberToJson(this);
}
