from app import db, User, followers

# Find duplicate follow relationships for a specific user (example: user_id = 1)
user_id = 1
duplicate_follows = db.session.query(followers).filter(followers.c.follower_id == user_id)\
                    .group_by(followers.c.followed_id)\
                    .having(db.func.count() > 1)\
                    .all()
# Remove duplicate follows for the user (assuming duplicate_follows contains the IDs to be removed)
for duplicate in duplicate_follows:
    db.session.delete(duplicate)
db.session.commit()
