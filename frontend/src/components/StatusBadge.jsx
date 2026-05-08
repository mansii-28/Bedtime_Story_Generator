export default function StatusBadge({ status }) {
  if (!status) return null;

  let label = status;
  let badgeClass = "status-badge ";

  if (status === "approved") {
    label = "✓ Approved";
    badgeClass += "status-approved";
  } else {
    label = "✗ " + status.replace(/_/g, " ");
    badgeClass += "status-failed";
  }

  return (
    <div className={badgeClass}>
      {label}
    </div>
  );
}
